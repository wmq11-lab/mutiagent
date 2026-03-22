from __future__ import annotations

from pathlib import Path

from mutiagent.llm.openai_client import available, get_base_url, get_model, get_provider, load_dotenv


def test_openai_defaults(monkeypatch) -> None:
    monkeypatch.delenv("MUTIAGENT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MUTIAGENT_LLM_MODEL", raising=False)
    monkeypatch.delenv("MUTIAGENT_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert get_provider() == "openai"
    assert get_model() == "gpt-4.1-mini"
    assert get_base_url() is None
    assert available() is False


def test_deepseek_provider_resolution(monkeypatch) -> None:
    monkeypatch.setenv("MUTIAGENT_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy")
    monkeypatch.delenv("MUTIAGENT_LLM_MODEL", raising=False)
    monkeypatch.delenv("MUTIAGENT_LLM_BASE_URL", raising=False)

    assert get_provider() == "deepseek"
    assert get_model() == "deepseek-chat"
    assert get_base_url() == "https://api.deepseek.com"
    assert available() is True


def test_zhipu_provider_resolution(monkeypatch) -> None:
    monkeypatch.setenv("MUTIAGENT_LLM_PROVIDER", "zhipu")
    monkeypatch.setenv("ZHIPU_API_KEY", "dummy")
    monkeypatch.delenv("MUTIAGENT_LLM_MODEL", raising=False)
    monkeypatch.delenv("MUTIAGENT_LLM_BASE_URL", raising=False)

    assert get_provider() == "zhipu"
    assert get_model() == "glm-4-flash"
    assert get_base_url() == "https://open.bigmodel.cn/api/paas/v4"
    assert available() is True


def test_load_dotenv_reads_repo_env_without_overriding_existing_env(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MUTIAGENT_LLM_PROVIDER", "openai")
    monkeypatch.setenv("MUTIAGENT_LLM_MODEL", "preset-model")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=from-dotenv\n"
        "MUTIAGENT_LLM_MODEL=dotenv-model\n",
        encoding="utf-8",
    )

    load_dotenv()

    assert get_provider() == "openai"
    assert get_model() == "preset-model"
    assert available() is True

    assert Path(".env").exists()


def test_available_respects_disable_flag(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MUTIAGENT_DISABLE_LLM", "1")
    assert available() is False
