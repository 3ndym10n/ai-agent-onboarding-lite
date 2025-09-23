"""
Unicode utilities for cross-platform compatibility.

This module provides utilities to handle Unicode characters safely across different
platforms and terminal encodings, particularly for Windows systems that may not
support Unicode emojis in the console.
"""

import os
import sys
from typing import Any, Dict, Optional

from ai_onboard.core.common_imports import Any, Dict, Optional, os, sys

# Emoji fallbacks for systems that don't support Unicode
EMOJI_FALLBACKS = {
    # Status indicators
    "✅": "[OK]",
    "❌": "[FAIL]",
    "⚠️": "[WARN]",
    "ℹ️": "[INFO]",
    "🟢": "[GOOD]",
    "🔴": "[BAD]",
    "🟡": "[PENDING]",
    "⭐": "[STAR]",
    "🎯": "[TARGET]",
    "🚀": "[LAUNCH]",
    "🔧": "[TOOL]",
    "📊": "[CHART]",
    "📈": "[TREND]",
    "🔍": "[SEARCH]",
    "💡": "[IDEA]",
    "⚡": "[FAST]",
    "🛡️": "[SHIELD]",
    "🔒": "[LOCK]",
    "🔓": "[UNLOCK]",
    "📝": "[NOTE]",
    "📋": "[LIST]",
    "📦": "[PACKAGE]",
    "🗂️": "[FOLDER]",
    "🎨": "[DESIGN]",
    "🧪": "[TEST]",
    "🔬": "[ANALYZE]",
    "⚙️": "[SETTINGS]",
    "🎲": "[RANDOM]",
    "🌟": "[FEATURE]",
    "🐛": "[BUG]",
    "🔥": "[HOT]",
    "❄️": "[COLD]",
    "💎": "[PREMIUM]",
    "🏆": "[WINNER]",
    "📊": "[METRICS]",
    "🎯": "[GOAL]",
    "🚨": "[ALERT]",
    "⏰": "[TIME]",
    "💻": "[CODE]",
    "🌐": "[WEB]",
    "📱": "[MOBILE]",
    "🖥️": "[DESKTOP]",
    "☁️": "[CLOUD]",
    "🔗": "[LINK]",
    "📡": "[SIGNAL]",
    "🎮": "[GAME]",
    "🎵": "[MUSIC]",
    "🎬": "[VIDEO]",
    "📷": "[PHOTO]",
    "🖼️": "[IMAGE]",
    "📄": "[DOC]",
    "📊": "[DATA]",
    "🗄️": "[DATABASE]",
    "🔐": "[SECURE]",
    "🛠️": "[REPAIR]",
    "⚖️": "[BALANCE]",
    "🎪": "[EVENT]",
    "🎭": "[THEATER]",
    "🎨": "[ART]",
    "🎯": "[PRECISION]",
    "🎲": "[CHANCE]",
    "🎳": "[STRIKE]",
    "🎸": "[MUSIC]",
    "🎺": "[TRUMPET]",
    "🥁": "[DRUMS]",
    "🎤": "[MIC]",
    "🎧": "[HEADPHONES]",
    "📻": "[RADIO]",
    "📺": "[TV]",
    "📹": "[CAMERA]",
    "📽️": "[PROJECTOR]",
    "🎞️": "[FILM]",
    "📀": "[CD]",
    "💿": "[DVD]",
    "💾": "[FLOPPY]",
    "💽": "[MINIDISC]",
    "🖨️": "[PRINTER]",
    "⌨️": "[KEYBOARD]",
    "🖱️": "[MOUSE]",
    "🖲️": "[TRACKBALL]",
    "💻": "[LAPTOP]",
    "🖥️": "[MONITOR]",
    "📟": "[PAGER]",
    "☎️": "[PHONE]",
    "📞": "[RECEIVER]",
    "📠": "[FAX]",
    "📧": "[EMAIL]",
    "📨": "[INCOMING]",
    "📩": "[OUTGOING]",
    "📪": "[MAILBOX]",
    "📫": "[MAIL]",
    "📬": "[OPEN_MAIL]",
    "📭": "[NO_MAIL]",
    "📮": "[POSTBOX]",
    "🗳️": "[BALLOT]",
    "✏️": "[PENCIL]",
    "✒️": "[PEN]",
    "🖋️": "[FOUNTAIN_PEN]",
    "🖊️": "[BALLPOINT]",
    "🖌️": "[PAINTBRUSH]",
    "🗒️": "[SPIRAL_NOTE]",
    "🗓️": "[SPIRAL_CALENDAR]",
    "📅": "[CALENDAR]",
    "📆": "[TEAR_OFF_CALENDAR]",
    "🗑️": "[WASTEBASKET]",
    "📇": "[CARD_INDEX]",
    "🗃️": "[CARD_FILE_BOX]",
    "🗄️": "[FILE_CABINET]",
    "📋": "[CLIPBOARD]",
    "📌": "[PUSHPIN]",
    "📍": "[ROUND_PUSHPIN]",
    "📎": "[PAPERCLIP]",
    "🖇️": "[LINKED_PAPERCLIPS]",
    "📏": "[STRAIGHT_RULER]",
    "📐": "[TRIANGULAR_RULER]",
    "✂️": "[SCISSORS]",
    "🗝️": "[OLD_KEY]",
    "🔨": "[HAMMER]",
    "🪓": "[AXE]",
    "⛏️": "[PICK]",
    "⚒️": "[HAMMER_AND_PICK]",
    "🛠️": "[HAMMER_AND_WRENCH]",
    "🗡️": "[DAGGER]",
    "⚔️": "[CROSSED_SWORDS]",
    "🔫": "[WATER_PISTOL]",
    "🪃": "[BOOMERANG]",
    "🏹": "[BOW_AND_ARROW]",
    "🛡️": "[SHIELD]",
    "🪚": "[CARPENTRY_SAW]",
    "🔧": "[WRENCH]",
    "🪛": "[SCREWDRIVER]",
    "🔩": "[NUT_AND_BOLT]",
    "⚙️": "[GEAR]",
    "🗜️": "[CLAMP]",
    "⚖️": "[BALANCE_SCALE]",
    "🦯": "[WHITE_CANE]",
    "🔗": "[LINK]",
    "⛓️": "[CHAINS]",
    "🪝": "[HOOK]",
    "🧰": "[TOOLBOX]",
    "🧲": "[MAGNET]",
    "🪜": "[LADDER]",
}


def is_unicode_supported() -> bool:
    """
    Check if the current terminal/console supports Unicode characters.

    Returns:
        bool: True if Unicode is supported, False otherwise
    """
    # Check if we're on Windows and using a console that might not support Unicode
    if os.name == "nt":
        try:
            # Try to encode a Unicode character
            "✅".encode(sys.stdout.encoding or "utf-8")
            return True
        except (UnicodeEncodeError, LookupError):
            return False

    # On Unix-like systems, assume Unicode is supported
    return True


def safe_print(text: str, **kwargs: Any) -> None:
    """
    Print text safely, falling back to ASCII alternatives for Unicode characters.

    Args:
        text: The text to print, potentially containing Unicode characters
        **kwargs: Additional keyword arguments to pass to print()
    """
    if is_unicode_supported():
        print(text, **kwargs)
    else:
        # Replace Unicode characters with ASCII alternatives
        safe_text = text
        for unicode_char, ascii_fallback in EMOJI_FALLBACKS.items():
            safe_text = safe_text.replace(unicode_char, ascii_fallback)
        print(safe_text, **kwargs)


def print_activity(message: str, **kwargs: Any) -> None:
    """
    Print an activity message with appropriate formatting.

    Args:
        message: The activity message to print
        **kwargs: Additional keyword arguments to pass to print()
    """
    safe_print(f"🔄 {message}", **kwargs)


def print_status(message: str, status: str = "info", **kwargs: Any) -> None:
    """
    Print a status message with appropriate emoji/indicator.

    Args:
        message: The message to print
        status: The status type ('ok', 'error', 'warn', 'info')
        **kwargs: Additional keyword arguments to pass to print()
    """
    status_icons = {
        "ok": "✅",
        "success": "✅",
        "error": "❌",
        "fail": "❌",
        "warn": "⚠️",
        "warning": "⚠️",
        "info": "ℹ️",
        "good": "🟢",
        "bad": "🔴",
        "pending": "🟡",
    }

    icon = status_icons.get(status.lower(), "ℹ️")
    safe_print(f"{icon} {message}", **kwargs)


def print_content(content: str, prefix: str = "", **kwargs: Any) -> None:
    """
    Print content with safe Unicode handling.

    Args:
        content: The content to print
        prefix: Optional prefix to add before each line
        **kwargs: Additional keyword arguments to pass to print()
    """
    if prefix:
        lines = content.split("\n")
        for line in lines:
            safe_print(f"{prefix}{line}", **kwargs)
    else:
        safe_print(content, **kwargs)


def get_safe_formatter():
    """
    Get a formatter function that handles Unicode safely.

    Returns:
        callable: A formatter function that handles Unicode appropriately
    """


    def safe_formatter(text: str) -> str:
        return format_with_fallback(text)

    return safe_formatter


def format_with_fallback(text: str, unicode_chars: Dict[str, str] = None) -> str:
    """
    Format text with Unicode characters, providing ASCII fallbacks if needed.

    Args:
        text: The text to format
        unicode_chars: Optional dictionary of Unicode characters to use

    Returns:
        str: The formatted text with appropriate character encoding
    """
    if unicode_chars is None:
        unicode_chars = EMOJI_FALLBACKS

    if is_unicode_supported():
        return text
    else:
        formatted_text = text
        for unicode_char, ascii_fallback in unicode_chars.items():
            formatted_text = formatted_text.replace(unicode_char, ascii_fallback)
        return formatted_text


def get_terminal_width() -> int:
    """
    Get the terminal width, with a sensible fallback.

    Returns:
        int: Terminal width in characters
    """
    try:
        import shutil

        return shutil.get_terminal_size().columns
    except (ImportError, OSError):
        return 80  # Sensible default


def create_separator(char: str = "─", width: int = None) -> str:
    """
    Create a separator line with safe Unicode handling.

    Args:
        char: The character to use for the separator
        width: The width of the separator (defaults to terminal width)

    Returns:
        str: A separator line
    """
    if width is None:
        width = get_terminal_width()

    # Use ASCII fallback if Unicode not supported
    if not is_unicode_supported():
        char = "-" if char in ["─", "━", "═"] else char

    return char * width


def print_separator(char: str = "─", width: int = None, **kwargs: Any) -> None:
    """
    Print a separator line with safe Unicode handling.

    Args:
        char: The character to use for the separator
        width: The width of the separator (defaults to terminal width)
        **kwargs: Additional keyword arguments to pass to print()
    """
    separator = create_separator(char, width)
    safe_print(separator, **kwargs)


def print_header(title: str, char: str = "═", **kwargs: Any) -> None:
    """
    Print a formatted header with safe Unicode handling.

    Args:
        title: The header title
        char: The character to use for the border
        **kwargs: Additional keyword arguments to pass to print()
    """
    width = get_terminal_width()

    # Use ASCII fallback if Unicode not supported
    if not is_unicode_supported():
        char = "=" if char in ["═", "━", "─"] else char

    border = char * width
    title_line = f" {title} ".center(width, char)

    safe_print("", **kwargs)
    safe_print(border, **kwargs)
    safe_print(title_line, **kwargs)
    safe_print(border, **kwargs)
    safe_print("", **kwargs)


def print_box(content: str, title: str = None, **kwargs: Any) -> None:
    """
    Print content in a box with safe Unicode handling.

    Args:
        content: The content to display in the box
        title: Optional title for the box
        **kwargs: Additional keyword arguments to pass to print()
    """
    lines = content.split("\n")
    max_line_length = max(len(line) for line in lines) if lines else 0
    width = min(max_line_length + 4, get_terminal_width())

    # Box drawing characters with ASCII fallbacks
    if is_unicode_supported():
        top_left, top_right = "┌", "┐"
        bottom_left, bottom_right = "└", "┘"
        horizontal, vertical = "─", "│"
        title_left, title_right = "┤", "├"
    else:
        top_left = top_right = bottom_left = bottom_right = "+"
        horizontal, vertical = "-", "|"
        title_left = title_right = "+"

    # Print top border
    if title:
        title_text = f" {title} "
        title_padding = width - len(title_text) - 2
        left_padding = title_padding // 2
        right_padding = title_padding - left_padding
        top_border = (
            top_left
            + horizontal * left_padding
            + title_left
            + title_text
            + title_right
            + horizontal * right_padding
            + top_right
        )
    else:
        top_border = top_left + horizontal * (width - 2) + top_right

    safe_print(top_border, **kwargs)

    # Print content lines
    for line in lines:
        padded_line = f"{vertical} {line:<{width-4}} {vertical}"
        safe_print(padded_line, **kwargs)

    # Print bottom border
    bottom_border = bottom_left + horizontal * (width - 2) + bottom_right
    safe_print(bottom_border, **kwargs)
