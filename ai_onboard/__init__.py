import os
from pathlib import Path

def _get_version():
    """Read version from VERSION file."""
    try:
        version_file = Path(__file__).parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return "0.2.2"  # Fallback version
    except Exception:
        return "0.2.2"  # Fallback version

__version__ = _get_version()
