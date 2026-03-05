import logging
import os

from langchain.chat_models import BaseChatModel

from src.config import get_app_config, get_tracing_config, is_tracing_enabled
from src.reflection import resolve_class

logger = logging.getLogger(__name__)


def _normalize_openai_settings(model_name: str, model_use: str, model_settings: dict, runtime_kwargs: dict) -> tuple[dict, dict]:
    """Normalize OpenAI api_key/base_url with config-first precedence and env fallback."""
    if model_use != "langchain_openai:ChatOpenAI":
        return model_settings, runtime_kwargs

    normalized_settings = dict(model_settings)
    normalized_runtime_kwargs = dict(runtime_kwargs)

    # Model config values take precedence over env fallback.
    api_key = normalized_settings.get("api_key")
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")

    base_url = normalized_settings.get("base_url")
    if base_url is None:
        base_url = os.getenv("OPENAI_BASE_URL")

    if api_key is None or not str(api_key).strip():
        raise ValueError(f"OpenAI api_key is required and cannot be empty for model '{model_name}' ({model_use})") from None

    if base_url is not None and not str(base_url).strip():
        raise ValueError(f"OpenAI base_url cannot be empty for model '{model_name}' ({model_use})") from None

    normalized_runtime_kwargs["api_key"] = str(api_key).strip()
    normalized_runtime_kwargs.pop("base_url", None)
    if base_url is not None:
        normalized_runtime_kwargs["base_url"] = str(base_url).strip()

    normalized_settings.pop("api_key", None)
    normalized_settings.pop("base_url", None)

    return normalized_settings, normalized_runtime_kwargs


def create_chat_model(name: str | None = None, thinking_enabled: bool = False, **kwargs) -> BaseChatModel:
    """Create a chat model instance from the config.

    Args:
        name: The name of the model to create. If None, the first model in the config will be used.

    Returns:
        A chat model instance.
    """
    config = get_app_config()
    if name is None:
        name = config.models[0].name
    model_config = config.get_model_config(name)
    if model_config is None:
        raise ValueError(f"Model {name} not found in config") from None
    model_class = resolve_class(model_config.use, BaseChatModel)
    model_settings_from_config = model_config.model_dump(
        exclude_none=True,
        exclude={
            "use",
            "name",
            "display_name",
            "description",
            "supports_thinking",
            "supports_reasoning_effort",
            "when_thinking_enabled",
            "supports_vision",
        },
    )
    if thinking_enabled and model_config.when_thinking_enabled is not None:
        if not model_config.supports_thinking:
            raise ValueError(f"Model {name} does not support thinking. Set `supports_thinking` to true in the `config.yaml` to enable thinking.") from None
        model_settings_from_config.update(model_config.when_thinking_enabled)
    if not thinking_enabled and model_config.when_thinking_enabled and model_config.when_thinking_enabled.get("extra_body", {}).get("thinking", {}).get("type"):
        kwargs.update({"extra_body": {"thinking": {"type": "disabled"}}})
        kwargs.update({"reasoning_effort": "minimal"})
    if not model_config.supports_reasoning_effort:
        kwargs.update({"reasoning_effort": None})
    model_settings_from_config, kwargs = _normalize_openai_settings(
        model_name=name,
        model_use=model_config.use,
        model_settings=model_settings_from_config,
        runtime_kwargs=kwargs,
    )

    try:
        model_instance = model_class(**kwargs, **model_settings_from_config)
    except Exception as e:
        raise ValueError(f"Failed to initialize model '{name}' with provider '{model_config.use}': {e}") from e

    if is_tracing_enabled():
        try:
            from langchain_core.tracers.langchain import LangChainTracer

            tracing_config = get_tracing_config()
            tracer = LangChainTracer(
                project_name=tracing_config.project,
            )
            existing_callbacks = model_instance.callbacks or []
            model_instance.callbacks = [*existing_callbacks, tracer]
            logger.debug(f"LangSmith tracing attached to model '{name}' (project='{tracing_config.project}')")
        except Exception as e:
            logger.warning(f"Failed to attach LangSmith tracing to model '{name}': {e}")
    return model_instance
