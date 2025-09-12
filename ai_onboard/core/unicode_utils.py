"""
Unicode utilities for cross-platform compatibility.

This module provides utilities to handle Unicode characters safely across different
platforms and terminal encodings, particularly for Windows systems that may not
support Unicode emojis in the console.
"""

import sys
import os
from typing import Dict, Any, Optional


# Emoji fallbacks for systems that don't support Unicode
EMOJI_FALLBACKS = {
    # Status indicators
    "✅": "[OK]",
    "❌": "[FAIL]", 
    "⚠️": "[WARN]",
    "ℹ️": "[INFO]",
    "🟢": "[GOOD]",
    "🟡": "[WARN]",
    "🔴": "[ERROR]",
    "⚪": "[INACTIVE]",
    "🟣": "[PENDING]",
    
    # Activity indicators  
    "🚀": "[START]",
    "🔄": "[SYNC]",
    "⏸️": "[PAUSE]",
    "⏹️": "[STOP]",
    "⏭️": "[SKIP]",
    "🔧": "[CONFIG]",
    "🛠️": "[TOOLS]",
    
    # Content indicators
    "📋": "[STATUS]",
    "📊": "[STATS]", 
    "📈": "[CHART]",
    "📄": "[FILE]",
    "📁": "[FOLDER]",
    "🗂️": "[DOCS]",
    "📝": "[NOTE]",
    "💡": "[TIP]",
    "🎯": "[TARGET]",
    "🔍": "[SEARCH]",
    "🧪": "[TEST]",
    "⭐": "[STAR]",
    "🔗": "[LINK]",
    
    # Progress indicators
    "▶️": "[PLAY]",
    "⏯️": "[PLAY/PAUSE]",
    "🔁": "[REPEAT]",
    "↩️": "[BACK]",
    "↪️": "[FORWARD]",
    "🔀": "[SHUFFLE]",
    
    # System indicators
    "💻": "[SYSTEM]",
    "🖥️": "[DESKTOP]",
    "📱": "[MOBILE]",
    "🌐": "[WEB]",
    "☁️": "[CLOUD]",
    "🔐": "[SECURE]",
    "🔓": "[UNLOCK]",
}


def is_unicode_supported() -> bool:
    """
    Check if the current environment supports Unicode output.
    
    Returns:
        bool: True if Unicode is supported, False otherwise
    """
    # Check if we're in a testing environment
    if os.environ.get("AI_ONBOARD_TEST_MODE"):
        return False  # Always use fallbacks in tests for consistency
    
    # Check Python version and encoding
    try:
        # Try to encode a simple emoji
        test_emoji = "✅"
        test_emoji.encode(sys.stdout.encoding or 'utf-8')
        
        # Check if stdout supports Unicode
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
            encoding = sys.stdout.encoding.lower()
            # These encodings typically don't support full Unicode
            if encoding in ['cp1252', 'ascii', 'latin-1']:
                return False
        
        return True
        
    except (UnicodeEncodeError, AttributeError, LookupError):
        return False


def safe_print(text: str, **kwargs) -> None:
    """
    Print text with Unicode fallbacks for incompatible systems.
    
    Args:
        text: The text to print (may contain Unicode characters)
        **kwargs: Additional arguments to pass to print()
    """
    if is_unicode_supported():
        try:
            print(text, **kwargs)
            return
        except UnicodeEncodeError:
            pass  # Fall through to fallback
    
    # Use fallbacks
    safe_text = text
    for emoji, fallback in EMOJI_FALLBACKS.items():
        safe_text = safe_text.replace(emoji, fallback)
    
    try:
        print(safe_text, **kwargs)
    except UnicodeEncodeError:
        # Last resort: encode to ASCII with replacement
        ascii_text = safe_text.encode('ascii', errors='replace').decode('ascii')
        print(ascii_text, **kwargs)


def safe_format(text: str) -> str:
    """
    Format text with Unicode fallbacks for incompatible systems.
    
    Args:
        text: The text to format (may contain Unicode characters)
        
    Returns:
        str: Text with Unicode characters replaced if necessary
    """
    if is_unicode_supported():
        return text
    
    # Use fallbacks
    safe_text = text
    for emoji, fallback in EMOJI_FALLBACKS.items():
        safe_text = safe_text.replace(emoji, fallback)
    
    return safe_text


def get_status_indicator(status: str) -> str:
    """
    Get a status indicator with Unicode fallback.
    
    Args:
        status: Status type ('success', 'error', 'warning', 'info')
        
    Returns:
        str: Unicode emoji or ASCII fallback
    """
    indicators = {
        'success': '✅',
        'error': '❌', 
        'warning': '⚠️',
        'info': 'ℹ️',
        'good': '🟢',
        'bad': '🔴',
        'pending': '🟡',
        'inactive': '⚪',
    }
    
    emoji = indicators.get(status.lower(), 'ℹ️')
    return safe_format(emoji)


def get_activity_indicator(activity: str) -> str:
    """
    Get an activity indicator with Unicode fallback.
    
    Args:
        activity: Activity type ('start', 'stop', 'sync', etc.)
        
    Returns:
        str: Unicode emoji or ASCII fallback
    """
    indicators = {
        'start': '🚀',
        'stop': '⏹️',
        'pause': '⏸️',
        'sync': '🔄',
        'config': '🔧',
        'test': '🧪',
        'search': '🔍',
    }
    
    emoji = indicators.get(activity.lower(), '▶️')
    return safe_format(emoji)


def get_content_indicator(content_type: str) -> str:
    """
    Get a content type indicator with Unicode fallback.
    
    Args:
        content_type: Content type ('status', 'stats', 'file', etc.)
        
    Returns:
        str: Unicode emoji or ASCII fallback
    """
    indicators = {
        'status': '📋',
        'stats': '📊',
        'chart': '📈', 
        'file': '📄',
        'folder': '📁',
        'docs': '🗂️',
        'note': '📝',
        'tip': '💡',
        'target': '🎯',
    }
    
    emoji = indicators.get(content_type.lower(), '📄')
    return safe_format(emoji)


class SafeFormatter:
    """A formatter that handles Unicode safely across platforms."""
    
    def __init__(self, use_unicode: Optional[bool] = None):
        """
        Initialize the formatter.
        
        Args:
            use_unicode: Force Unicode on/off, or None for auto-detection
        """
        self.use_unicode = use_unicode if use_unicode is not None else is_unicode_supported()
    
    def format(self, text: str) -> str:
        """Format text with Unicode safety."""
        if self.use_unicode:
            return text
        return safe_format(text)
    
    def print(self, text: str, **kwargs) -> None:
        """Print text with Unicode safety."""
        safe_print(text, **kwargs)
    
    def status(self, message: str, status: str = 'info') -> str:
        """Format a status message."""
        indicator = get_status_indicator(status)
        return f"{indicator} {message}"
    
    def activity(self, message: str, activity: str = 'start') -> str:
        """Format an activity message."""
        indicator = get_activity_indicator(activity)
        return f"{indicator} {message}"
    
    def content(self, message: str, content_type: str = 'info') -> str:
        """Format a content message."""
        indicator = get_content_indicator(content_type)
        return f"{indicator} {message}"


# Global formatter instance
_formatter = SafeFormatter()


def get_safe_formatter() -> SafeFormatter:
    """Get the global safe formatter instance."""
    return _formatter


def configure_unicode_support(force_ascii: bool = False) -> None:
    """
    Configure Unicode support globally.
    
    Args:
        force_ascii: If True, force ASCII-only output
    """
    global _formatter
    _formatter = SafeFormatter(use_unicode=not force_ascii)


# Convenience functions
def print_status(message: str, status: str = 'info', **kwargs) -> None:
    """Print a status message with safe Unicode handling."""
    formatted = _formatter.status(message, status)
    _formatter.print(formatted, **kwargs)


def print_activity(message: str, activity: str = 'start', **kwargs) -> None:
    """Print an activity message with safe Unicode handling."""
    formatted = _formatter.activity(message, activity)
    _formatter.print(formatted, **kwargs)


def print_content(message: str, content_type: str = 'info', **kwargs) -> None:
    """Print a content message with safe Unicode handling."""
    formatted = _formatter.content(message, content_type)
    _formatter.print(formatted, **kwargs)


if __name__ == "__main__":
    # Test the Unicode utilities
    print("Testing Unicode utilities...")
    print(f"Unicode supported: {is_unicode_supported()}")
    
    print("\nTesting safe printing:")
    safe_print("✅ This should work on all systems")
    safe_print("📋 Project Status - Unicode test")
    safe_print("🚀 Starting process...")
    
    print("\nTesting formatter:")
    formatter = get_safe_formatter()
    formatter.print(formatter.status("Test successful", "success"))
    formatter.print(formatter.activity("Testing activity", "test"))
    formatter.print(formatter.content("Status information", "status"))
