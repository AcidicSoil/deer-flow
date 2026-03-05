import pytest

from src.config.app_config import AppConfig


def test_resolve_env_variables_raises_when_openai_api_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Environment variable OPENAI_API_KEY not found"):
        AppConfig.resolve_env_variables({"api_key": "$OPENAI_API_KEY"})


def test_resolve_env_variables_raises_when_openai_api_key_empty(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "   ")

    with pytest.raises(ValueError, match="Environment variable OPENAI_API_KEY is empty"):
        AppConfig.resolve_env_variables({"api_key": "$OPENAI_API_KEY"})


def test_resolve_env_variables_raises_when_openai_base_url_whitespace(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "\t  ")

    with pytest.raises(ValueError, match="Environment variable OPENAI_BASE_URL is empty"):
        AppConfig.resolve_env_variables({"base_url": "$OPENAI_BASE_URL"})


def test_resolve_env_variables_keeps_non_openai_behavior(monkeypatch):
    monkeypatch.setenv("CUSTOM_ENV", "   ")

    resolved = AppConfig.resolve_env_variables({"value": "$CUSTOM_ENV"})

    assert resolved["value"] == "   "
