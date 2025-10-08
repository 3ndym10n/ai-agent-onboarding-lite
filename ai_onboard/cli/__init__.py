"""CLI package initialization.

We set a global safe print hook the first time any CLI module is imported.
This keeps legacy modules that call ``print`` directly working while
ensuring Windows consoles (cp1252) do not crash on emoji-heavy output.
"""

from __future__ import annotations

import builtins

from .console import safe_print


if getattr(builtins, "_ai_onboard_safe_print_enabled", False) is not True:
    builtins.print = safe_print  # type: ignore[assignment]
    builtins._ai_onboard_safe_print_enabled = True
