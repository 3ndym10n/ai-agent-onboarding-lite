"""
Console output helpers that degrade gracefully on terminals without UTF-8 support.

Windows consoles default to cp1252, which raises `UnicodeEncodeError` when printing
emoji-heavy status messages. These helpers fall back to ASCII-friendly substitutes,
keeping output readable for vibe coders on older setups.
"""

import os
from typing import Dict


_BUILTIN_PRINT = print

# Map common emoji (explicit unicode escapes) to readable ASCII fallbacks.
_ASCII_FALLBACKS: Dict[str, str] = {
    "\U0001F680": "[INIT]",
    "\u2705": "[OK]",
    "\U0001F4CA": "[STATUS]",
    "\U0001F3AF": "[NEXT]",
    "\u274C": "[ERROR]",
    "\U0001F4C8": "[DATA]",
    "\U0001F6E0": "[TOOLS]",
    "\U0001F6E0\uFE0F": "[TOOLS]",
    "\U0001F916": "[AGENT]",
    "\U0001F91D": "[READY]",
    "\u26A1": "[EXEC]",
    "\U0001F4DD": "[INFO]",
    "\U0001F5C2": "[SESSIONS]",
    "\U0001F5C2\uFE0F": "[SESSIONS]",
    "\U0001F527": "[CONFIG]",
    "\U0001F4CB": "[LIST]",
    "\U0001F3D7": "[CONTEXT]",
    "\U0001F3D7\uFE0F": "[CONTEXT]",
    "\u2699": "[LIMITS]",
    "\u2699\uFE0F": "[LIMITS]",
    "\U0001F524": "[TRANSLATE]",
    "\U0001F4A1": "[TIP]",
}


def _prefer_ascii() -> bool:
    """Decide if we should avoid emoji output."""
    if os.environ.get("AI_ONBOARD_ASCII", "").lower() in {"1", "true", "yes"}:
        return True
    if os.name == "nt" and os.environ.get("PYTHONUTF8") != "1":
        return True
    return False


def _apply_fallbacks(message: str) -> str:
    """Replace known emoji with ASCII stand-ins before printing."""
    normalized = message
    for symbol, replacement in _ASCII_FALLBACKS.items():
        normalized = normalized.replace(symbol, replacement)
    return normalized


def safe_print(message: str = "", *args, **kwargs) -> None:
    """
    Print text with graceful fallback to ASCII replacements when needed.

    Attempts to print the original message first. If the terminal rejects
    the output (UnicodeEncodeError) or the environment prefers ASCII,
    we swap in the fallback text so execution never crashes.
    """

    text = str(message)

    if _prefer_ascii():
        text = _apply_fallbacks(text)

    try:
        _BUILTIN_PRINT(text, *args, **kwargs)
        return
    except UnicodeEncodeError:
        pass

    # Terminal still refused. Force ASCII-safe output to avoid crashing.
    fallback = _apply_fallbacks(text)
    fallback = fallback.encode("ascii", "replace").decode("ascii")
    _BUILTIN_PRINT(fallback, *args, **kwargs)
