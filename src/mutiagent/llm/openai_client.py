from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    default_model: str
    default_base_url: str | None
    api_key_envs: tuple[str, ...]


_PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "openai": ProviderConfig(
        provider="openai",
        default_model="gpt-4.1-mini",
        default_base_url=None,
        api_key_envs=("OPENAI_API_KEY",),
    ),
    "deepseek": ProviderConfig(
        provider="deepseek",
        default_model="deepseek-chat",
        default_base_url="https://api.deepseek.com",
        api_key_envs=("DEEPSEEK_API_KEY", "OPENAI_API_KEY"),
    ),
    "zhipu": ProviderConfig(
        provider="zhipu",
        default_model="glm-4-flash",
        default_base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_envs=("ZHIPU_API_KEY", "OPENAI_API_KEY"),
    ),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _candidate_env_files() -> list[Path]:
    candidates: list[Path] = []
    cwd_env = Path.cwd() / ".env"
    repo_env = _repo_root() / ".env"
    for path in (cwd_env, repo_env):
        if path not in candidates:
            candidates.append(path)
    return candidates


def load_dotenv() -> None:
    for env_file in _candidate_env_files():
        if not env_file.exists():
            continue
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key or key in os.environ:
                continue
            if value and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            os.environ[key] = value
        return


load_dotenv()


def _get_provider_config() -> ProviderConfig:
    provider = os.getenv("MUTIAGENT_LLM_PROVIDER", "openai").strip().lower()
    return _PROVIDER_CONFIGS.get(provider, _PROVIDER_CONFIGS["openai"])


def _get_api_key() -> str:
    cfg = _get_provider_config()
    for env_name in cfg.api_key_envs:
        value = os.getenv(env_name)
        if value:
            return value
    return ""


def get_provider() -> str:
    return _get_provider_config().provider


def get_base_url() -> str | None:
    cfg = _get_provider_config()
    return os.getenv("MUTIAGENT_LLM_BASE_URL") or cfg.default_base_url


def _client() -> OpenAI:
    kwargs: dict[str, Any] = {"api_key": _get_api_key()}
    base_url = get_base_url()
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def get_model() -> str:
    cfg = _get_provider_config()
    return os.getenv("MUTIAGENT_LLM_MODEL") or os.getenv("MUTIAGENT_OPENAI_MODEL", cfg.default_model)


def chat_messages(messages: list[dict[str, str]], *, temperature: float = 0.3) -> str:
    """
    多轮对话：messages 为 OpenAI Chat 格式，须包含 role（system/user/assistant）与 content。
    """
    api_key = _get_api_key()
    if not api_key:
        cfg = _get_provider_config()
        raise RuntimeError(f"缺少 API Key 环境变量，请配置：{' / '.join(cfg.api_key_envs)}")

    c = _client()
    resp = c.chat.completions.create(
        model=get_model(),
        temperature=temperature,
        messages=messages,
    )
    return (resp.choices[0].message.content or "").strip()


def chat_text(system: str, user: str, *, temperature: float = 0.2) -> str:
    api_key = _get_api_key()
    if not api_key:
        cfg = _get_provider_config()
        raise RuntimeError(f"缺少 API Key 环境变量，请配置：{' / '.join(cfg.api_key_envs)}")

    return chat_messages(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )


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
    if os.getenv("MUTIAGENT_DISABLE_LLM", "").strip().lower() in {"1", "true", "yes", "on"}:
        return False
    return bool(_get_api_key())
 
