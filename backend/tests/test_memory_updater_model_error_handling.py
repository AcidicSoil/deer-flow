import logging
from unittest.mock import MagicMock

from langchain_core.messages import HumanMessage

from src.agents.memory import updater as updater_module
from src.agents.memory.updater import MemoryUpdater


def test_update_memory_logs_model_init_failure_and_returns_false(monkeypatch, caplog):
    updater = MemoryUpdater(model_name="memory-model")

    monkeypatch.setattr(updater_module, "get_memory_data", lambda agent_name=None: updater_module._create_empty_memory())
    monkeypatch.setattr(updater_module, "format_conversation_for_update", lambda messages: "User: hello")
    monkeypatch.setattr(MemoryUpdater, "_get_model", lambda self: (_ for _ in ()).throw(RuntimeError("init failed")))

    with caplog.at_level(logging.ERROR):
        ok = updater.update_memory([HumanMessage(content="hello")])

    assert ok is False
    assert "Failed to initialize memory update model" in caplog.text
    assert "init failed" in caplog.text


def test_update_memory_logs_model_invoke_failure_and_returns_false(monkeypatch, caplog):
    updater = MemoryUpdater(model_name="memory-model")

    fake_model = MagicMock()
    fake_model.invoke.side_effect = RuntimeError("invoke failed")

    monkeypatch.setattr(updater_module, "get_memory_data", lambda agent_name=None: updater_module._create_empty_memory())
    monkeypatch.setattr(updater_module, "format_conversation_for_update", lambda messages: "User: hello")
    monkeypatch.setattr(MemoryUpdater, "_get_model", lambda self: fake_model)

    with caplog.at_level(logging.ERROR):
        ok = updater.update_memory([HumanMessage(content="hello")])

    assert ok is False
    assert "Failed to invoke memory update model" in caplog.text
    assert "invoke failed" in caplog.text
