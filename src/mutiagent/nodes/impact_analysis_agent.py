from __future__ import annotations

import logging
import math
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from mutiagent.graph.state import (
    ChangeRecord,
    ExecutableTestStrategy,
    FileChangeSummary,
    ImpactGraphFile,
    ImpactGraphSymbol,
    ImpactTestFocusDerived,
    ImpactTestPlanEntry,
    SemanticUnit,
    SemanticUnitType,
    TestPriorityTier,
    TopRiskEntry,
    WorkflowState,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 日志（调试）
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _impact_log_file_path() -> Path:
    log_dir = _repo_root() / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "impact_analysis_agent.log"


def _impact_debug_enabled() -> bool:
    return os.getenv("MUTIAGENT_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def _impact_debug_log(message: str) -> None:
    if not _impact_debug_enabled():
        return
    line = f"[ImpactAnalysisAgent] {message}"
    print(line, file=sys.stderr, flush=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _impact_log_file_path().open("a", encoding="utf-8") as fp:
            fp.write(f"{timestamp} {line}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 1) 语义剪枝
# ---------------------------------------------------------------------------

_PRUNE_SEED_NAMES_LOWER: frozenset[str] = frozenset(
    {
        "split",
        "strip",
        "startswith",
        "endswith",
        "replace",
        "join",
        "lower",
        "upper",
        "json",
        "loads",
        "dumps",
        "len",
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "set",
        "tuple",
        "range",
        "enumerate",
        "zip",
        "map",
        "filter",
        "print",
        "open",
        "isinstance",
        "hasattr",
        "getattr",
        "setattr",
        "type",
        "super",
        "object",
        "self",
        "cls",
        "true",
        "false",
        "none",
        "if",
        "else",
        "return",
        "pass",
        "and",
        "or",
        "not",
        "in",
        "for",
        "while",
    }
)


def _should_prune_seed(seed_name: str, seed_kind: str) -> bool:
    """判断 impact_seed 是否应丢弃：内置/字符串工具/过短标识等。"""
    n = (seed_name or "").strip()
    if len(n) <= 1:
        return True
    nl = n.lower()
    if nl in _PRUNE_SEED_NAMES_LOWER:
        return True
    if seed_kind == "dependency" and nl in _PRUNE_SEED_NAMES_LOWER:
        return True
    return False


# ---------------------------------------------------------------------------
# 2) 语义单元类型推断
# ---------------------------------------------------------------------------


def _infer_unit_type_from_seed_text(name: str, kind: str) -> SemanticUnitType | None:
    """由 seed 名称 + kind 推断单元类型；无法归类且应保留时由调用方默认 data_processing。"""
    t = f"{name} {kind}".lower()
    if re.search(r"getenv|environ|dotenv|configparser|settings\.|base_url|api_key|secret", t):
        return "config"
    if re.search(r"raise|error|exception|valueerror|typeerror|httperror|abort", t):
        return "exception"
    if re.search(
        r"\brequest\b|post\(|\.post\b|\bget\(|\.get\b|put\(|patch\(|delete\(|httpx|fetch|grpc|client\.|urllib",
        t,
    ):
        return "api"
    # 下划线/驼峰内的 llm 子串（如 build_llm_params）也视为 API 相关
    if re.search(r"llm|multimodal|chat_completion|embedding|tokenizer", t):
        return "api"
    if re.search(r"\bjson\b|parse|yaml|schema|validate|serialize|pickle|csv|xml", t):
        return "data_processing"
    if kind == "dependency" and not _should_prune_seed(name, kind):
        return "api"
    return None


def _infer_unit_types_from_semantic_tags(tags: list[str]) -> list[SemanticUnitType]:
    """由 semantic_tags 映射补充语义单元类型（聚合列表，V4 原子行优先用 _unit_type_for_semantic_tag）。"""
    out: list[SemanticUnitType] = []
    s = set(tags)
    if s & {"input_validation_added", "null_check_added", "exception_handling_changed"}:
        out.append("exception")
    if s & {"dependency_call_changed", "api_signature_changed"}:
        out.append("api")
    if s & {"logic_branch_changed", "return_value_changed"}:
        out.append("data_processing")
    return out


def _unit_type_for_semantic_tag(tag: str) -> SemanticUnitType | None:
    """单条 semantic_tag → 语义类型（用于原子 semantic_unit）。"""
    if tag in ("input_validation_added", "null_check_added", "exception_handling_changed"):
        return "exception"
    if tag in ("dependency_call_changed", "api_signature_changed"):
        return "api"
    if tag in ("logic_branch_changed", "return_value_changed"):
        return "data_processing"
    return None


# ---------------------------------------------------------------------------
# 3) 规则驱动的 test_focus
# ---------------------------------------------------------------------------


def _rule_derived_test_focus(unit_type: SemanticUnitType) -> list[ImpactTestFocusDerived]:
    """按语义单元类型挂载测试关注点，每条带规则来源。"""
    rules: dict[SemanticUnitType, list[tuple[str, str]]] = {
        "config": [
            ("env_missing", "规则：type=config → 覆盖环境变量缺失"),
            ("fallback", "规则：type=config → 覆盖默认值 / 配置回退"),
        ],
        "exception": [
            ("error_paths", "规则：type=exception → 覆盖错误分支与非法输入"),
            ("exception_assertion", "规则：type=exception → 断言异常类型与信息"),
        ],
        "api": [
            ("retry", "规则：type=api → 覆盖重试与退避"),
            ("timeout", "规则：type=api → 覆盖超时行为"),
            ("mock", "规则：type=api → 对外部 IO 使用 mock/stub"),
        ],
        "data_processing": [
            ("boundary", "规则：type=data_processing → 边界值与空输入"),
            ("invalid_input", "规则：type=data_processing → 非法格式/解析失败"),
        ],
    }
    return [ImpactTestFocusDerived(type=a, derived_from=b) for a, b in rules.get(unit_type, [])]


# ---------------------------------------------------------------------------
# 4) 语义感知的可执行 test_strategy（避免 API 模板千篇一律）
# ---------------------------------------------------------------------------


def _build_semantic_strategies(
    unit_type: SemanticUnitType,
    label_symbol: str,
    file_path: str,
    source_hint: str,
) -> list[ExecutableTestStrategy]:
    """
    根据 source_hint / 符号名生成差异化策略（streaming、config 细分、内外部异常等）。
    """
    hint = f"{source_hint} {label_symbol} {file_path}".lower()
    base = f"{file_path}::{label_symbol}"

    if unit_type == "config":
        strats: list[ExecutableTestStrategy] = []
        if re.search(r"getenv|environ|os\.environ", hint):
            strats.append(
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：未设置关键环境变量时的行为（env 路径）",
                    input="使用 monkeypatch.delenv 删除约定变量名后调用",
                    mock="monkeypatch / patch.dict(os.environ, clear=True) 局部清除",
                    assert_="应抛出明确 ConfigurationError/ValueError 或使用文档记载的默认值",
                )
            )
        if re.search(r"dotenv|load_dotenv|\.env", hint):
            strats.append(
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：.env 缺失或与进程环境冲突时的优先级",
                    input="无 .env 文件；或 .env 与 export 变量同时存在",
                    mock="临时目录 + 空/残缺 .env 文件；patch 加载路径",
                    assert_="应遵循「进程环境覆盖文件」或产品约定顺序，且可观测",
                )
            )
        if re.search(r"override|argv|cli|argparse", hint) or not strats:
            strats.append(
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：显式配置覆盖默认/回退（override 路径）",
                    input="在同时提供默认值与显式参数/配置文件时调用",
                    mock="patch 配置源顺序，制造后写覆盖先写",
                    assert_="显式配置优先生效；回退链路与文档一致",
                )
            )
        if len(strats) < 2:
            strats.append(
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：配置项类型或范围非法",
                    input="注入非数字端口、空 URL、负数超时等",
                    mock="patch 配置读取返回值",
                    assert_="拒绝非法配置并失败可测，不应静默继续",
                )
            )
        return strats[:4]

    if unit_type == "exception":
        ext = bool(re.search(r"httperror|connection|timeout|requests|httpx|grpc|socket|external", hint))
        if ext:
            return [
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：外部依赖失败（网络/HTTP）向上游暴露",
                    input="触发下游 HTTP 5xx 或连接重置",
                    mock="responses / MockTransport 模拟外部错误",
                    assert_="应包装为领域异常或明确错误码，不吞掉原始可诊断信息",
                ),
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：外部超时与重试边界",
                    input="正常入参",
                    mock="第一次调用 timeout，第二次成功（若实现有重试）",
                    assert_="超时后行为符合重试策略；无重试则应快速失败",
                ),
            ]
        return [
            ExecutableTestStrategy(
                scenario=f"{label_symbol}：入参校验失败（内部异常路径）",
                input="None、空集合、违反不变量的结构体",
                mock="无需外网",
                assert_="抛出 ValueError/TypeError 等与类型注解一致的异常",
            ),
            ExecutableTestStrategy(
                scenario=f"{label_symbol}：不变量破坏时的断言与错误消息",
                input="构造违反业务规则的中间状态",
                mock="必要时 patch 内部依赖返回非法组合",
                assert_="异常信息包含可定位字段（字段名/错误码）",
            ),
        ]

    if unit_type == "api":
        strats_api: list[ExecutableTestStrategy] = []
        if "_stream" in hint or "stream" in hint or "streaming" in hint:
            strats_api.append(
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：流式响应中途取消/客户端断开",
                    input="消费 generator/async iterator 若干 chunk 后关闭",
                    mock="模拟 client 中断或 asyncio.CancelledError",
                    assert_="资源释放（连接/文件句柄）；无悬挂任务；错误可观测",
                )
            )
        if re.search(r"oauth|bearer|authorization|api_key", hint):
            strats_api.append(
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：鉴权头缺失或过期",
                    input="省略 Authorization 或注入过期 token",
                    mock="stub 401/403 响应",
                    assert_="应清晰区分未授权与禁止访问，不重试不可恢复 401（除非实现刷新 token）",
                )
            )
        strats_api.extend(
            [
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：依赖服务返回 5xx / 连接错误",
                    input="可达 URL 但服务端错误",
                    mock="MockTransport 返回 500",
                    assert_="重试策略或失败快速暴露；无无限阻塞",
                ),
                ExecutableTestStrategy(
                    scenario=f"{label_symbol}：请求超时",
                    input="正常参数",
                    mock="挂起响应直至 timeout",
                    assert_="在配置超时内失败并抛出可捕获超时异常",
                ),
            ]
        )
        # 去重 scenario 前缀过于相似时保留前 4 条
        seen: set[str] = set()
        out: list[ExecutableTestStrategy] = []
        for s in strats_api:
            key = s.scenario[:48]
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
            if len(out) >= 4:
                break
        return out

    return [
        ExecutableTestStrategy(
            scenario=f"{label_symbol} 数据解析/校验（{base}）",
            input="合法边界、空输入、畸形片段",
            mock="隔离文件与网络",
            assert_="合法通过；非法显式失败",
        ),
    ]


# ---------------------------------------------------------------------------
# 5) 风险分与 priority_score 中间量
# ---------------------------------------------------------------------------


def _change_weight_intent(intent: str) -> float:
    """变更意图权重。"""
    return {"BUG_FIX": 1.0, "FEATURE": 0.74, "REFACTOR": 0.58}.get(intent, 0.65)


def _semantic_weight(unit_type: SemanticUnitType) -> float:
    """语义类别权重。"""
    return {"config": 1.1, "exception": 1.14, "api": 1.02, "data_processing": 0.76}[unit_type]


def _tag_risk_multiplier(tags: list[str]) -> float:
    """semantic_tags 微调。"""
    m = 1.0
    for t in tags:
        if t in ("null_check_added", "input_validation_added", "exception_handling_changed"):
            m *= 1.06
        if t == "logic_branch_changed":
            m *= 1.04
        if t == "api_signature_changed":
            m *= 1.05
    return min(m, 1.12)


def _compute_layered_risk_score(
    intent: str,
    unit_type: SemanticUnitType,
    propagation_depth: int,
    semantic_tags: list[str],
) -> float:
    """risk_score：与 V2 一致的压缩区间，供 priority_score 乘算。"""
    cw = _change_weight_intent(intent)
    decay = 0.88 ** max(0, propagation_depth)
    sw = _semantic_weight(unit_type)
    rw = _tag_risk_multiplier(semantic_tags)
    raw = cw * decay * sw * rw * 0.42
    return max(0.14, min(0.89, raw))


def _split_symbol_id(symbol_id: str) -> tuple[str, str, str]:
    """解析 symbol_id = file:type:entity（从右侧切分，兼容路径中含冒号）。"""
    parts = symbol_id.rsplit(":", 2)
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return symbol_id, "function", symbol_id


def _label_from_symbol_id(symbol_id: str) -> str:
    """取 entity 名用于策略文案。"""
    return _split_symbol_id(symbol_id)[2]


def _atomic_slug_from_seed(kind: str, name: str) -> str:
    """V4：单 seed → 短 slug（过长时取末尾若干段），避免多行为拼成一条 id。"""
    base = (name or "").strip()
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", base)
    parts = [p.lower() for p in re.split(r"[_\s.]+", s1) if p and len(p) < 48]
    if len(parts) > 5:
        parts = parts[-4:]
    slug = "_".join(parts)[:48] or "generic"
    slug = re.sub(r"[^a-z0-9_]+", "_", slug).strip("_")
    return slug or "generic"


def _atomic_slug_from_semantic_tag(tag: str) -> str:
    """单条 tag → 短 slug（去 _changed/_added 等后缀）。"""
    t = tag.replace("_changed", "").replace("_added", "").replace("_removed", "")
    parts = [p for p in t.split("_") if p]
    if len(parts) > 4:
        parts = parts[-3:]
    slug = "_".join(parts)[:40].lower()
    slug = re.sub(r"[^a-z0-9_]+", "_", slug).strip("_")
    return slug or "tag"


def _make_atomic_semantic_unit_id(unit_type: SemanticUnitType, source: str) -> str:
    """由单条 source（seed:… 或 semantic_tag:…）生成全局 semantic_unit_id。"""
    if source.startswith("seed:"):
        tail = source[5:]
        if ":" not in tail:
            return f"{unit_type}:generic"
        kind, name = tail.split(":", 1)
        slug = _atomic_slug_from_seed(kind, name)
    elif source.startswith("semantic_tag:"):
        tag = source[13:]
        slug = _atomic_slug_from_semantic_tag(tag)
    else:
        slug = "generic"
    return f"{unit_type}:{slug}"


def _parse_seed_names_from_sources(sources: list[str]) -> list[str]:
    """提取 seed 中的名称（小写）用于跨符号关联。"""
    names: list[str] = []
    for s in sources:
        if not s.startswith("seed:"):
            continue
        tail = s[5:]
        if ":" not in tail:
            continue
        kind, name = tail.split(":", 1)
        if _should_prune_seed(name, kind):
            continue
        n = name.strip().lower()
        if n:
            names.append(n)
    return names


def _seed_occurrence_index(state: WorkflowState) -> dict[str, list[tuple[str, str]]]:
    """seed 名 -> [(file, symbol_id), ...]，用于 1~2 跳跨文件传播。"""
    idx: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for fs in state.change_analysis:
        for ch in fs.changes:
            sid = f"{fs.file}:{ch.type}:{ch.entity}"
            for sd in ch.impact_seeds:
                if _should_prune_seed(sd.name, sd.kind):
                    continue
                idx[sd.name.strip().lower()].append((fs.file, sid))
    return idx


def _compute_centrality_mult(downstream_count: int, chain_len: int) -> float:
    """调用链中心性乘子：1.2 / 1.0 / 0.8。"""
    if downstream_count >= 2 or chain_len >= 4:
        return 1.2
    if downstream_count >= 1 or chain_len >= 2:
        return 1.0
    return 0.8


def _assign_test_priority(
    unit_type: SemanticUnitType,
    priority_score_norm: float,
) -> TestPriorityTier:
    """
    P0：config / exception / 外部 API；
    P1：高优先级 data_processing；
    P2：其余低风险数据处理。
    """
    if unit_type in ("config", "exception", "api"):
        return "P0"
    if unit_type == "data_processing":
        return "P1" if priority_score_norm >= 0.52 else "P2"
    return "P2"


# ---------------------------------------------------------------------------
# 6) V4 原子行：每个 seed / 每条 semantic_tag 各对应一条语义单元
# ---------------------------------------------------------------------------


def _atomic_rows_for_change(ch: ChangeRecord) -> list[tuple[SemanticUnitType, str]]:
    """返回 (unit_type, single_source) 列表，一条原子能力一行。"""
    rows: list[tuple[SemanticUnitType, str]] = []
    for sd in ch.impact_seeds:
        if _should_prune_seed(sd.name, sd.kind):
            continue
        ut = _infer_unit_type_from_seed_text(sd.name, sd.kind)
        if ut is None:
            ut = "data_processing"
        rows.append((ut, f"seed:{sd.kind}:{sd.name}"))
    for tag in ch.semantic_tags:
        ut = _unit_type_for_semantic_tag(tag)
        if ut is not None:
            rows.append((ut, f"semantic_tag:{tag}"))
    return rows


@dataclass
class _UnitAcc:
    """合并相同 semantic_unit_id 的累加器。"""

    unit_id: str
    unit_type: SemanticUnitType
    sources: set[str] = field(default_factory=set)
    symbol_ids: set[str] = field(default_factory=set)
    files: set[str] = field(default_factory=set)
    risk_max: float = 0.0
    propagation_depth_max: int = 0


def _merge_accruals(
    per_symbol_rows: list[tuple[str, str, ChangeRecord, SemanticUnitType, list[str], int]],
) -> dict[str, _UnitAcc]:
    """
    per_symbol_rows: (file, symbol_id, change, ut, source_list, depth)，source_list 仅含 1 条原子 source。
    按 atomic semantic_unit_id 合并。
    """
    acc: dict[str, _UnitAcc] = {}
    for file_path, sym_id, ch, ut, src_list, depth in per_symbol_rows:
        src0 = src_list[0] if src_list else "seed:variable:generic"
        uid = _make_atomic_semantic_unit_id(ut, src0)
        if uid not in acc:
            acc[uid] = _UnitAcc(unit_id=uid, unit_type=ut)
        a = acc[uid]
        a.sources.add(src0)
        a.symbol_ids.add(sym_id)
        a.files.add(file_path)
        r = _compute_layered_risk_score(ch.intent, ut, depth, ch.semantic_tags)
        a.risk_max = max(a.risk_max, r)
        a.propagation_depth_max = max(a.propagation_depth_max, depth)
    return acc


def _edge_types_for_unit(ut: SemanticUnitType, sources: list[str]) -> list[str]:
    """V4：由类型与来源打边标签。"""
    tags: set[str] = set()
    if ut == "config":
        tags.add("config")
    if ut in ("api", "exception"):
        tags.add("call")
    if ut == "data_processing":
        tags.add("data")
    for s in sources:
        if s.startswith("semantic_tag:"):
            tags.add("call")
    return sorted(tags)


def _finalize_catalog_units(state: WorkflowState, acc_map: dict[str, _UnitAcc]) -> list[SemanticUnit]:
    """V4：priority_score 公式 + 映射 0.2~0.9；upstream 反推；edge_types。"""
    seed_idx = _seed_occurrence_index(state)
    changed_set = set(state.changed_files)

    prelim: dict[str, dict[str, float | list[str] | bool | str]] = {}

    for uid, a in acc_map.items():
        src_str = "; ".join(sorted(a.sources))[:2000]
        seed_names = _parse_seed_names_from_sources(list(a.sources))
        primary_sid = min(a.symbol_ids)
        pf, _, _ = _split_symbol_id(primary_sid)

        downstream_ids: list[str] = []
        for sn in seed_names:
            hits = seed_idx.get(sn, [])
            cross_first = sorted(
                hits,
                key=lambda x: (0 if x[0] != pf else 1, x[1]),
            )
            for _f2, sid2 in cross_first:
                if sid2 == primary_sid:
                    continue
                if sid2 not in downstream_ids:
                    downstream_ids.append(sid2)
                if len(downstream_ids) >= 5:
                    break
            if len(downstream_ids) >= 5:
                break

        chain = [primary_sid] + downstream_ids[:4]
        integration = len({f for f in a.files}) > 1 or any(_split_symbol_id(d)[0] != pf for d in downstream_ids)

        ref_n = len(a.symbol_ids)
        log_refs = math.log(1.0 + float(max(0, ref_n)))

        direct_touch = bool(a.files & changed_set) if changed_set else True
        change_mult = 1.5 if direct_touch else 1.0

        cent_mult = _compute_centrality_mult(len(downstream_ids), len(chain))
        integ_mult = 1.3 if integration else 1.0

        raw_p = float(a.risk_max) * change_mult * cent_mult * log_refs * integ_mult
        prelim[uid] = {
            "src_str": src_str,
            "chain": chain,
            "downstream": downstream_ids,
            "integration": integration,
            "raw_p": raw_p,
            "risk": float(a.risk_max),
            "cent_mult": cent_mult,
            "change_mult": change_mult,
            "log_refs": log_refs,
            "integ_mult": integ_mult,
            "prop_depth": float(a.propagation_depth_max),
        }

    if not prelim:
        return []

    raws = [float(prelim[u]["raw_p"]) for u in prelim]
    mn, mx = min(raws), max(raws)
    span = mx - mn

    sorted_by_raw = sorted(prelim.keys(), key=lambda u: (-float(prelim[u]["raw_p"]), u))

    p_norm_by_uid: dict[str, float] = {}
    n = len(sorted_by_raw)
    for rank, uid in enumerate(sorted_by_raw):
        raw_p = float(prelim[uid]["raw_p"])
        if span < 1e-9:
            if n <= 1:
                p_norm = 0.55
            else:
                p_norm = round(0.2 + 0.7 * rank / (n - 1), 4)
        else:
            p_norm = round(0.2 + 0.7 * (raw_p - mn) / span, 4)
        p_norm = max(0.2, min(0.9, p_norm))
        # 微扰避免完全同分：在 raw 有差异时仍可能四舍五入碰撞，按 rank 加极小 epsilon
        jitter = (n - 1 - rank) * 1e-6
        p_norm = round(min(0.9, p_norm + jitter), 6)
        p_norm_by_uid[uid] = p_norm

    upstream_by_target: dict[str, list[str]] = defaultdict(list)
    for uid in prelim:
        primary = min(acc_map[uid].symbol_ids)
        for d in prelim[uid]["downstream"]:
            if isinstance(d, str):
                upstream_by_target[d].append(primary)

    catalog: list[SemanticUnit] = []
    label_sym = _label_from_symbol_id

    for uid, a in acc_map.items():
        meta = prelim[uid]
        src_str = str(meta["src_str"])
        chain = meta["chain"]
        downstream = meta["downstream"]
        integration = bool(meta["integration"])
        risk = float(meta["risk"])
        cent_mult = float(meta["cent_mult"])
        p_norm = p_norm_by_uid[uid]

        ut = a.unit_type
        tpri = _assign_test_priority(ut, p_norm)
        primary_sid = min(a.symbol_ids)
        sym_label = label_sym(primary_sid)
        upstream_list = sorted(set(upstream_by_target.get(primary_sid, [])))
        edges = _edge_types_for_unit(ut, list(a.sources))

        unit = SemanticUnit(
            semantic_unit_id=uid,
            type=ut,
            source=src_str,
            risk_score=round(risk, 4),
            priority_score=p_norm,
            test_priority=tpri,
            centrality_factor=round(cent_mult, 3),
            call_chain=list(chain),
            downstream=list(downstream),
            upstream=upstream_list,
            edge_types=edges,
            integration_risk=integration,
            referenced_symbol_ids=sorted(a.symbol_ids),
            propagation_depth=a.propagation_depth_max,
            test_focus=_rule_derived_test_focus(ut),
            test_strategy=_build_semantic_strategies(ut, sym_label, _split_symbol_id(primary_sid)[0], src_str),
        )
        catalog.append(unit)

    catalog.sort(key=lambda u: (-u.priority_score, u.semantic_unit_id))
    return catalog


def _symbol_centrality(symbol_unit_ids: list[str], uid_to_unit: dict[str, SemanticUnit]) -> float:
    """符号级：多单元或含集成风险时提高枢纽分。"""
    if not symbol_unit_ids:
        return 0.8
    if len(symbol_unit_ids) >= 3:
        return 1.2
    if any(uid_to_unit[i].integration_risk for i in symbol_unit_ids if i in uid_to_unit):
        return 1.15
    if len(symbol_unit_ids) >= 2:
        return 1.05
    return 1.0


def _build_impact_test_plan(graph: list[ImpactGraphFile], uid_to_unit: dict[str, SemanticUnit]) -> list[ImpactTestPlanEntry]:
    entries: list[ImpactTestPlanEntry] = []
    tier_rank = {"P0": 0, "P1": 1, "P2": 2}

    for gf in graph:
        for sym in gf.symbols:
            units = [uid_to_unit[i] for i in sym.semantic_unit_ids if i in uid_to_unit]
            if not units:
                continue
            best_tier = min((u.test_priority for u in units), key=lambda t: tier_rank.get(t, 3))
            types_set: set[str] = set()
            for u in units:
                if u.type == "api":
                    types_set.update(["integration", "mock"])
                elif u.type == "config":
                    types_set.update(["integration", "env"])
                elif u.type == "exception":
                    types_set.add("exception")
                else:
                    types_set.add("unit")
            if any(u.integration_risk for u in units):
                types_set.add("integration")
            sem_count = len(sym.semantic_unit_ids)
            avg_ps = sum(u.priority_score for u in units) / len(units)
            integ_mul = 1.5 if any(u.integration_risk for u in units) else 1.0
            est = max(1, int(round(sem_count * avg_ps * integ_mul)))
            reason_parts = [
                f"语义单元：{', '.join(sorted({u.type for u in units}))}",
                f"estimated_cases={sem_count}×avg_priority×{'1.5' if integ_mul > 1 else '1.0'}",
            ]
            if any(u.integration_risk for u in units):
                reason_parts.append("存在跨文件/多模块调用链（integration 风险）")
            reason_parts.append(f"最高测试优先级 {best_tier}（按 config/exception/api 优先规则）")
            max_ps = max(u.priority_score for u in units)
            entries.append(
                (
                    tier_rank.get(best_tier, 3),
                    -max_ps,
                    ImpactTestPlanEntry(
                        target=sym.name,
                        symbol_id=sym.symbol_id,
                        priority=best_tier,  # type: ignore[arg-type]
                        test_types=sorted(types_set),
                        estimated_cases=est,
                        reason="；".join(reason_parts),
                    ),
                )
            )

    entries.sort(key=lambda x: (x[0], x[1]))
    return [e[2] for e in entries]


def _priority_score_debug_top5(catalog: list[SemanticUnit]) -> list[dict[str, str | float]]:
    """debug：按 priority_score 排序的 Top5。"""
    top = sorted(catalog, key=lambda u: (-u.priority_score, u.semantic_unit_id))[:5]
    out: list[dict[str, str | float]] = []
    for u in top:
        bits = [f"score={u.priority_score:.4f}", f"risk={u.risk_score:.3f}"]
        if u.integration_risk:
            bits.append("integration")
        if u.centrality_factor >= 1.15:
            bits.append("hub")
        out.append({"semantic_unit_id": u.semantic_unit_id, "priority_score": u.priority_score, "reason": "; ".join(bits)})
    return out


def _build_top_risks(catalog: list[SemanticUnit], limit: int = 12) -> list[TopRiskEntry]:
    """V4：高风险集合（priority + integration 等）。"""
    ranked = sorted(catalog, key=lambda u: (-u.priority_score, u.semantic_unit_id))
    out: list[TopRiskEntry] = []
    for u in ranked[:limit]:
        parts: list[str] = [f"priority_score={u.priority_score:.3f}"]
        if u.integration_risk:
            parts.append("integration 风险")
        if u.centrality_factor >= 1.15:
            parts.append("调用链枢纽")
        if len(u.referenced_symbol_ids) >= 2:
            parts.append(f"多符号引用×{len(u.referenced_symbol_ids)}")
        reason = "；".join(parts) if len(parts) > 1 else f"高 priority_score（{u.priority_score:.3f}）"
        out.append(TopRiskEntry(semantic_unit_id=u.semantic_unit_id, reason=reason))
    return out


def build_impact_graph(state: WorkflowState) -> tuple[list[ImpactGraphFile], list[SemanticUnit]]:
    """
    构建 V4：原子 semantic_unit + 全局 catalog + impact_graph（符号仅持 id）。
    返回 (impact_graph, catalog)。
    """
    per_symbol_rows: list[tuple[str, str, ChangeRecord, SemanticUnitType, list[str], int]] = []

    for fs in state.change_analysis:
        if not fs.changes:
            continue
        for ch in fs.changes:
            sym_id = f"{fs.file}:{ch.type}:{ch.entity}"
            for ut, src1 in _atomic_rows_for_change(ch):
                per_symbol_rows.append((fs.file, sym_id, ch, ut, [src1], 0))

    acc_map = _merge_accruals(per_symbol_rows)
    catalog = _finalize_catalog_units(state, acc_map)
    uid_to_unit = {u.semantic_unit_id: u for u in catalog}

    graph: list[ImpactGraphFile] = []
    for fs in state.change_analysis:
        if not fs.changes:
            continue
        symbols: list[ImpactGraphSymbol] = []
        for ch in fs.changes:
            sym_id = f"{fs.file}:{ch.type}:{ch.entity}"
            uids: list[str] = []
            for ut, src1 in _atomic_rows_for_change(ch):
                uid = _make_atomic_semantic_unit_id(ut, src1)
                if uid in uid_to_unit:
                    uids.append(uid)
            uids = sorted(set(uids))
            if not uids:
                continue
            cent = _symbol_centrality(uids, uid_to_unit)
            symbols.append(
                ImpactGraphSymbol(
                    name=ch.entity,
                    entity_type=ch.type,
                    symbol_id=sym_id,
                    semantic_unit_ids=uids,
                    centrality=round(cent, 3),
                )
            )
        if symbols:
            graph.append(ImpactGraphFile(file=fs.file, symbols=symbols))

    return graph, catalog


def _impact_debug_stats_v3(graph: list[ImpactGraphFile], catalog: list[SemanticUnit]) -> dict:
    type_dist: dict[str, int] = defaultdict(int)
    for u in catalog:
        type_dist[u.type] += 1
    return {
        "semantic_unit_catalog_count": len(catalog),
        "symbol_count": sum(len(gf.symbols) for gf in graph),
        "file_count": len(graph),
        "impact_type_distribution": dict(sorted(type_dist.items(), key=lambda x: (-x[1], x[0]))),
        "test_focus_count": sum(len(u.test_focus) for u in catalog),
    }


def analyze_impact(state: WorkflowState) -> WorkflowState:
    """
    Impact V4：原子语义单元、priority_score 梯度、upstream/edge_types、impact_test_plan、top_risks。
    平铺 impacted / impacted_ranked 仍清空。
    """
    started = time.perf_counter()
    graph, catalog = build_impact_graph(state)
    uid_to_unit = {u.semantic_unit_id: u for u in catalog}

    state.impact_graph = graph
    state.semantic_units_catalog = catalog
    state.impact_test_plan = _build_impact_test_plan(graph, uid_to_unit)
    state.top_risks = _build_top_risks(catalog)
    state.impacted = []
    state.impacted_ranked = []

    stats = _impact_debug_stats_v3(graph, catalog)
    elapsed = round(time.perf_counter() - started, 3)
    top_n = int(os.getenv("MUTIAGENT_IMPACT_TOP_N", "15") or 15)
    top_ids = [u.semantic_unit_id for u in catalog[: max(1, top_n)]]

    _impact_debug_log(
        f"impact_v4 files={stats['file_count']} symbols={stats['symbol_count']} "
        f"catalog_units={stats['semantic_unit_catalog_count']} elapsed_s={elapsed}"
    )

    refine = os.getenv("MUTIAGENT_IMPACT_LLM_REFINE", "").strip().lower() in {"1", "true", "yes", "on"}
    state.debug["impact"] = {
        "mode": "impact_graph_v4",
        "candidate_count": 0,
        "ranked_count": 0,
        "used_llm": False,
        "change_graph_used": state.change_graph is not None,
        "propagation_hops_max": int(os.getenv("MUTIAGENT_IMPACT_MAX_PROPAGATION_HOPS", "3") or 3),
        "semantic_unit_catalog_count": stats["semantic_unit_catalog_count"],
        "impact_test_plan_count": len(state.impact_test_plan),
        "top_priority_semantic_unit_ids": top_ids,
        "priority_score_top_5": _priority_score_debug_top5(catalog),
        "impact_type_distribution": stats["impact_type_distribution"],
        "ranking_mode": "v4_risk_x_change_x_centrality_x_logrefs_x_integration_mapped_0.2_0.9",
        "llm_error": None,
        "elapsed_seconds": elapsed,
        "llm_refine_enabled": refine,
        "note": "V4：semantic_units_catalog（原子 id）+ upstream/edge_types + impact_test_plan + top_risks",
    }
    return state


# build_impact_graph 返回 (impact_graph, catalog)，调用方需解包
