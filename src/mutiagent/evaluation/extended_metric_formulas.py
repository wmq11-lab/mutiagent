"""
扩展实验指标：公式说明 + 纯函数封装 + 完整实现入口（一站式导入）。

本文件把 ``compute_extended_experiment_metrics`` 及相关模块里**可写成初等公式**的部分
抽成纯函数，便于写报告/论文时对照；涉及 diff、coverage.json、AST、pytest 收集的完整计算
仍通过下方 re-export 的函数完成（与主流程代码一致）。

------------------------------------------------------------------------------
1. 变更行覆盖率（changed_line_coverage_pct / Recall on changed ``+`` lines）
------------------------------------------------------------------------------

与 ``change_line_coverage_from_diff_and_cov_paths`` 一致::

    recall_frac = covered_plus_lines / change_plus_lines

- ``change_plus_lines``：unified diff 中，符合条件的生产侧 ``.py`` 文件（路径不含 ``tests``
  目录段）里，补丁块中 ``+`` 行（非 ``+++``）对应的行号数量汇总。
- ``covered_plus_lines``：上述行号中，落在当次 ``coverage.json`` 记录的**已执行行**集合
  内的条数。

百分数（主流程写法）::

    changed_line_coverage_pct = round(recall_frac * 100, 3)   # 无有效分母时为 None

------------------------------------------------------------------------------
2. 新增函数覆盖率（added_function_coverage_pct）
------------------------------------------------------------------------------

对每个待统计的新增函数（见 ``compute_added_function_coverage_pct`` 的 specs 来源：
``CHANGED_FUNCS``、diff 中 ``+`` 行的 ``def``、或 change_analysis 中 ADD 的
function/method）::

- 若能在数据集工作区解析到该函数体行号区间 ``[lo, hi]``，且 coverage 中该文件存在
  任意已执行行 ``ln in [lo, hi]``，则计入 ``added_function_covered``。
- 若无法解析到区间，仍 ``added_function_total += 1``（视为未覆盖）。

::

    added_function_coverage_pct = round(100 * added_function_covered / added_function_total, 3)

------------------------------------------------------------------------------
3. 跨模块测试数（cross_module_test_case_count）
------------------------------------------------------------------------------

**非单一分数公式**：对每个生成文件中的 ``test_*``（及 ``async def test_*``），在 AST 上
收集 import 与 ``ast.Call`` 调用链所触及的、落在「变更文件集合」中的相对路径数
``|touched|``；若 ``|touched| >= 2`` 则该用例计 1。变更文件少于 2 个时结果为 0。
严格 AST 计数为 0 时，可回退到宽松子串匹配（见 ``_cross_module_loose_substring_count``）。

实现：``compute_cross_module_test_cases``（``extended_experiment_metrics``）。

------------------------------------------------------------------------------
4. 测试用例压缩率（test_case_compression_pct）
------------------------------------------------------------------------------

::

    test_case_compression_pct = round((1 - G / C) * 100, 3)

- ``G`` = ``generated_test_function_count``（生成/选中的测试函数数）
- ``C`` = ``pytest --collect-only`` 解析得到的工程内 collected 用例数（> 0）

------------------------------------------------------------------------------
5. 执行时间压缩率 / 墙钟缩减（exec_time_reduction_pct）
------------------------------------------------------------------------------

::

    exec_time_reduction_pct = round((1 - T_sel / T_full) * 100, 3)

- ``T_sel``：本次子集运行的 pytest 墙钟（从合并输出解析 ``... in Xs`` 最后一条，或 junit
  summary 的时间字段兜底）。
- ``T_full``：全量套件墙钟（缓存文件或 ``MUTIAGENT_MEASURE_FULL_SUITE_TIME=1`` 实测）。

无全量墙钟时，可用粗估 ``T_full ≈ T_sel * (C / G)`` 再代入上式（见
``compute_extended_experiment_metrics`` 中注释）。

**注意**：``metrics.time_reduction`` 是另一路指标，定义为比例 ``1 - execution_time / full_time``
（0~1），用于 evaluation 核心字典中的 ``time_reduction``，与这里的**百分数**
``exec_time_reduction_pct`` 命名相近但用途不同。

------------------------------------------------------------------------------
6. Bug detection rate（bug_detection_rate_pct）
------------------------------------------------------------------------------

令 ``F`` 为失败用例 id 列表（``FAILING_TESTS`` 环境变量，或 junit 中 failed/error 用例）；
``S`` 为 ``selected_tests`` 经路径规范化 + casefold 后的集合::

    bug_detection_rate_pct = round(100 * |{ f ∈ F : norm(f) ∈ S }| / |F|, 3)

无失败基准（``|F| = 0``）时，主流程记 ``None`` 并在 note 中标注 N/A。
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# 纯公式（仅依赖计数/时间，便于单测与对外说明）
# ---------------------------------------------------------------------------


def changed_line_recall_frac(covered_plus_lines: int, change_plus_lines: int) -> float | None:
    """与 ``change_line_coverage_from_diff_and_cov_paths`` 返回的 ``recall_frac`` 一致。"""
    if change_plus_lines <= 0:
        return None
    return round(float(covered_plus_lines) / float(change_plus_lines), 6)


def changed_line_coverage_percent(covered_plus_lines: int, change_plus_lines: int) -> float | None:
    """对应 ``compute_extended_experiment_metrics`` 中的 ``changed_line_coverage_pct``。"""
    r = changed_line_recall_frac(covered_plus_lines, change_plus_lines)
    return None if r is None else round(r * 100.0, 3)


def added_function_coverage_percent(covered: int, total: int) -> float | None:
    """对应 ``compute_added_function_coverage_pct`` 聚合后的百分数口径。"""
    if total <= 0:
        return None
    return round(100.0 * float(covered) / float(total), 3)


def test_case_compression_percent(
    generated_test_function_count: int,
    project_collected_test_count: int,
) -> float | None:
    """对应 ``test_case_compression_pct``。"""
    if project_collected_test_count <= 0:
        return None
    return round((1.0 - float(generated_test_function_count) / float(project_collected_test_count)) * 100.0, 3)


def exec_time_reduction_percent(selected_wall_seconds: float, full_suite_wall_seconds: float) -> float | None:
    """对应 ``exec_time_reduction_pct``（百分数）。"""
    if full_suite_wall_seconds <= 0:
        return None
    return round((1.0 - float(selected_wall_seconds) / float(full_suite_wall_seconds)) * 100.0, 3)


def _norm_casefold_id(x: str) -> str:
    return (x or "").strip().replace("\\", "/").casefold()


def bug_detection_rate_percent(
    failing_test_ids: list[str],
    selected_tests: list[str] | None,
) -> tuple[float | None, int, int, int]:
    """
    返回 ``(pct, hit_count, failing_count, selected_distinct_count)``。

    ``pct`` 与 ``compute_extended_experiment_metrics`` 的 ``bug_detection_rate_pct`` 一致；
    ``selected_distinct_count`` 为规范化后的 selected 集合大小（便于调试）。
    """
    sel = {_norm_casefold_id(x) for x in (selected_tests or []) if str(x).strip()}
    if not failing_test_ids:
        return None, 0, 0, len(sel)
    hit = sum(1 for fe in failing_test_ids if _norm_casefold_id(fe) in sel)
    denom = len(failing_test_ids)
    if denom <= 0:
        return None, hit, 0, len(sel)
    return round(100.0 * float(hit) / float(denom), 3), hit, denom, len(sel)


def parse_pytest_wall_seconds_last(combined_pytest_output: str) -> float | None:
    """
    与 ``extended_experiment_metrics._parse_pytest_duration_seconds`` 同款语义：
    取输出中 ``in Xs`` 最后一处匹配的 ``X``。
    """
    blob = combined_pytest_output or ""
    matches = list(re.finditer(r"\bin\s+(\d+(?:\.\d+)?)\s*s\b", blob, re.I))
    if not matches:
        return None
    return float(matches[-1].group(1))


# ---------------------------------------------------------------------------
# 完整实现：与主流程相同的模块入口（避免复制大段 AST/diff 逻辑）
# ---------------------------------------------------------------------------

from mutiagent.evaluation.change_line_coverage import (  # noqa: E402
    change_line_coverage_from_diff_and_cov_paths,
)
from mutiagent.evaluation.extended_experiment_metrics import (  # noqa: E402
    compute_added_function_coverage_pct,
    compute_cross_module_test_cases,
    compute_extended_experiment_metrics,
)

REFERENCE_IMPLEMENTATION: dict[str, Any] = {
    "changed_line_coverage": change_line_coverage_from_diff_and_cov_paths,
    "added_function_coverage": compute_added_function_coverage_pct,
    "cross_module_test_count": compute_cross_module_test_cases,
    "full_extended_block": compute_extended_experiment_metrics,
}

__all__ = [
    "REFERENCE_IMPLEMENTATION",
    "added_function_coverage_percent",
    "bug_detection_rate_percent",
    "changed_line_coverage_percent",
    "changed_line_recall_frac",
    "compute_added_function_coverage_pct",
    "compute_cross_module_test_cases",
    "compute_extended_experiment_metrics",
    "change_line_coverage_from_diff_and_cov_paths",
    "exec_time_reduction_percent",
    "parse_pytest_wall_seconds_last",
    "test_case_compression_percent",
]
