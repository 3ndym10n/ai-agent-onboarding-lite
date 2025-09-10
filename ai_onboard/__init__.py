try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development/editable installs
    try:
        from pathlib import Path

        version_file = Path(__file__).parent / "VERSION.txt"
        if version_file.exists():
            __version__ = version_file.read_text().strip()
        else:
            __version__ = "0.2.2"
    except Exception:
        __version__ = "0.2.2"
