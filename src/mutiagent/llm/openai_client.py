from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


def _client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_model() -> str:
    return os.getenv("MUTIAGENT_OPENAI_MODEL", "gpt-4.1-mini")


def chat_text(system: str, user: str, *, temperature: float = 0.2) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY 环境变量")

    c = _client()
    resp = c.chat.completions.create(
        model=get_model(),
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


def chat_json(system: str, user: str, *, temperature: float = 0.2) -> dict[str, Any]:
    """
    尽量从 LLM 输出中解析 JSON 对象；解析失败则抛错。
    """
    text = chat_text(system, user, temperature=temperature)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"无法在LLM输出中定位JSON对象：{text[:2000]}")
    blob = text[start : end + 1]
    return json.loads(blob)


def available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))
 
