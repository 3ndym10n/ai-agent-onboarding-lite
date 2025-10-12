import argparse
from pathlib import Path

from ai_onboard.cli import commands_cursor
from ai_onboard.core.ai_integration import cursor_ai_integration as cursor_module


def test_cursor_guided_setup_creates_session(tmp_path, capsys):
    """Smoke test the guided setup flow for Cursor integration."""

    # Ensure a fresh integration instance that points at the temp project root.
    cursor_module._cursor_integration = None
    root: Path = tmp_path

    args = argparse.Namespace(user_id="smoke_user", force_init=False, skip_session=False)

    commands_cursor._handle_cursor_guided_setup(args, root)

    out = capsys.readouterr().out
    assert "Cursor Guided Setup" in out
    assert "Guided setup complete" in out

    integration = cursor_module.get_cursor_integration(root)
    sessions = integration.list_active_sessions()

    assert sessions["success"] is True
    assert sessions["count"] >= 1

    # Clean up the singleton for any downstream tests.
    cursor_module._cursor_integration = None
