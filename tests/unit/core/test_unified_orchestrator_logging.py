import logging

from ai_onboard.core.orchestration import unified_tool_orchestrator as uto


def test_log_fallback_respects_environment(monkeypatch, caplog):
    """_log_fallback should emit output only when debugging flag is enabled."""

    logger_name = uto.__name__
    caplog.set_level(logging.INFO, logger=logger_name)

    uto._log_fallback("component_a", "fallback_impl")
    assert "component_a" not in caplog.text

    monkeypatch.setenv("AI_ONBOARD_DEBUG_FALLBACKS", "1")
    uto._log_fallback("component_b", "fallback_impl")
    assert "component_b" in caplog.text

    monkeypatch.delenv("AI_ONBOARD_DEBUG_FALLBACKS", raising=False)
