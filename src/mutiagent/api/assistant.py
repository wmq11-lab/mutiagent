from __future__ import annotations

import json
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from mutiagent.llm.openai_client import available as llm_available
from mutiagent.llm.openai_client import chat_messages

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

_MAX_CONTEXT_CHARS = 14_000
_MAX_HISTORY_MSG = 16


class AssistantMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=12_000)


class AssistantChatRequest(BaseModel):
    messages: list[AssistantMessage] = Field(..., min_length=1, max_length=32)
    context: Optional[dict[str, Any]] = Field(
        default=None,
        description="前端打包的当前分析会话摘要（changed_files、evaluation、top_risks 等）",
    )


class AssistantChatResponse(BaseModel):
    reply: str
    used_llm: bool = False
    note: Optional[str] = None


def _compact_context(ctx: dict[str, Any] | None) -> str:
    if not ctx:
        return "{}"
    try:
        s = json.dumps(ctx, ensure_ascii=False)
    except (TypeError, ValueError):
        s = str(ctx)
    if len(s) > _MAX_CONTEXT_CHARS:
        s = s[:_MAX_CONTEXT_CHARS] + "\n…(已截断)"
    return s


def _fallback_reply(last_user: str, ctx: dict[str, Any] | None) -> str | None:
    if not last_user.strip():
        return None
    text = last_user.strip()
    ev = (ctx or {}).get("evaluation") or {}
    rd = ev.get("report_dir") if isinstance(ev, dict) else None
    files = (ctx or {}).get("changed_files") or []
    risks = (ctx or {}).get("top_risks") or []
    paths = (ctx or {}).get("generated_test_paths") or []

    if any(k in text for k in ("报告", "report", "pytest", "junit", "html")):
        if rd:
            return (
                "根据当前会话数据，测试报告已生成在目标仓库本地目录：\n\n"
                f"{rd}\n\n"
                "请在本机用资源管理器或 IDE 打开该路径下的 **report.html**（以及同目录的 junit.xml、pytest 日志等）。\n"
                "浏览器无法直接访问你磁盘上的 file:// 路径，需本地打开文件。"
            )
        if ev.get("ran") is False:
            return "当前数据里未执行 pytest（可能未勾选 run_eval）。请先在「代码变更」中勾选执行测试并重新运行全流程。"
        return "当前会话中还没有 report_dir。请先完成一次全流程且开启 run_eval；若已执行失败，请到「执行结果」查看退出码与日志。"

    if any(k in text for k in ("影响", "模块", "哪些", "范围", "波及")):
        if not files:
            return "当前没有已缓存的分析结果。请先在「代码变更」页粘贴 diff 并运行全流程，再问影响范围。"
        lines = [f"- 变更文件共 **{len(files)}** 个："]
        for f in files[:40]:
            lines.append(f"  - `{f}`")
        if len(files) > 40:
            lines.append("  - …")
        if risks:
            lines.append("\n高风险语义单元（节选）：")
            for r in risks[:10]:
                if isinstance(r, dict):
                    lines.append(f"  - `{r.get('semantic_unit_id', '')}`：{r.get('reason', '')[:120]}")
        return "\n".join(lines)

    if any(k in text for k in ("用例", "测试代码", "生成测试", "pytest 文件")):
        if paths:
            return (
                "当前会话已生成测试文件（路径如下）。请到侧栏 **Test Cases / 用例中心** 查看与编辑完整代码，或导出 JSON：\n\n"
                + "\n".join(f"- `{p}`" for p in paths[:12])
            )
        return (
            "尚未检测到已生成的测试文件。请在「代码变更」页填写仓库路径与 diff，点击 **运行全流程**；"
            "生成完成后在 **用例中心** 查看。若关闭了 LLM，系统可能只生成占位 smoke 用例。"
        )

    return None


_SYSTEM_PROMPT = """你是 mutiagent 多智能体测试工作台的中文 AI 助理。

用户正在使用：代码变更 → 影响分析 → 测试策略 → 用例生成 → 执行与报告。

规则：
1) 严格依据「当前界面上下文」JSON 回答；没有的数据请明确说「需要先运行全流程」或「上下文中无此项」，不要编造路径或文件。
2) 测试报告：若上下文中 evaluation.report_dir 存在，告诉用户在本机打开该目录下的 report.html（说明浏览器无法直接打开本地磁盘路径）。
3) 影响模块：结合 changed_files、impact_summary、top_risks 说明，条理清晰。
4) 生成测试用例：若已有 generated_test_paths 或内容摘要，引导用户到「用例中心」查看完整代码；否则说明如何触发全流程。
5) 回答简洁，使用短段落与列表，避免冗长套话。"""


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(req: AssistantChatRequest) -> AssistantChatResponse:
    ctx = req.context if isinstance(req.context, dict) else None
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")

    if llm_available():
        ctx_block = _compact_context(ctx or {})
        system = _SYSTEM_PROMPT + "\n\n【当前界面上下文】\n```json\n" + ctx_block + "\n```"
        hist: list[dict[str, str]] = [{"role": "system", "content": system}]
        for m in req.messages[-_MAX_HISTORY_MSG:]:
            hist.append({"role": m.role, "content": m.content})
        try:
            reply = chat_messages(hist, temperature=0.35)
        except Exception as e:
            fb = _fallback_reply(last_user, ctx)
            if fb:
                return AssistantChatResponse(
                    reply=fb,
                    used_llm=False,
                    note=f"模型调用失败，已使用规则回复：{e!s}",
                )
            raise HTTPException(status_code=502, detail=f"模型调用失败：{e!s}") from e
        return AssistantChatResponse(reply=reply, used_llm=True)

    fb = _fallback_reply(last_user, ctx)
    if fb:
        return AssistantChatResponse(
            reply=fb,
            used_llm=False,
            note="当前未配置 LLM 或已禁用（MUTIAGENT_DISABLE_LLM），此为规则助理回复。",
        )

    raise HTTPException(
        status_code=503,
        detail="未配置 LLM API Key，且无法根据关键词生成规则回复。请配置 .env 中的 Key，或提出与报告/影响/用例相关的问题。",
    )
