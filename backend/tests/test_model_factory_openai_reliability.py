import pytest

from src.config.app_config import AppConfig
from src.config.model_config import ModelConfig
from src.config.sandbox_config import SandboxConfig
from src.models import factory as factory_module


class _FakeModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.callbacks = []


def _make_app_config(*, api_key=None, base_url=None):
    model_kwargs = {
        "name": "openai-test",
        "display_name": "OpenAI Test",
        "description": None,
        "use": "langchain_openai:ChatOpenAI",
        "model": "gpt-4o-mini",
        "supports_thinking": False,
        "supports_vision": False,
    }
    if api_key is not None:
        model_kwargs["api_key"] = api_key
    if base_url is not None:
        model_kwargs["base_url"] = base_url

    return AppConfig(
        models=[ModelConfig(**model_kwargs)],
        sandbox=SandboxConfig(use="src.sandbox.local:LocalSandboxProvider"),
    )


def test_create_chat_model_uses_config_values_over_env(monkeypatch):
    app_config = _make_app_config(api_key="cfg-key", base_url="https://cfg.example/v1")

    monkeypatch.setattr(factory_module, "get_app_config", lambda: app_config)
    monkeypatch.setattr(factory_module, "resolve_class", lambda use, base: _FakeModel)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://env.example/v1")

    model = factory_module.create_chat_model(name="openai-test")

    assert model.kwargs["api_key"] == "cfg-key"
    assert model.kwargs["base_url"] == "https://cfg.example/v1"


def test_create_chat_model_falls_back_to_env(monkeypatch):
    app_config = _make_app_config()

    monkeypatch.setattr(factory_module, "get_app_config", lambda: app_config)
    monkeypatch.setattr(factory_module, "resolve_class", lambda use, base: _FakeModel)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://env.example/v1")

    model = factory_module.create_chat_model(name="openai-test")

    assert model.kwargs["api_key"] == "env-key"
    assert model.kwargs["base_url"] == "https://env.example/v1"


def test_create_chat_model_requires_non_empty_effective_api_key(monkeypatch):
    app_config = _make_app_config()

    monkeypatch.setattr(factory_module, "get_app_config", lambda: app_config)
    monkeypatch.setattr(factory_module, "resolve_class", lambda use, base: _FakeModel)
    monkeypatch.setenv("OPENAI_API_KEY", "  ")

    with pytest.raises(ValueError, match="api_key is required and cannot be empty"):
        factory_module.create_chat_model(name="openai-test")


def test_create_chat_model_rejects_empty_effective_base_url(monkeypatch):
    app_config = _make_app_config()

    monkeypatch.setattr(factory_module, "get_app_config", lambda: app_config)
    monkeypatch.setattr(factory_module, "resolve_class", lambda use, base: _FakeModel)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "   ")

    with pytest.raises(ValueError, match="base_url cannot be empty"):
        factory_module.create_chat_model(name="openai-test")
