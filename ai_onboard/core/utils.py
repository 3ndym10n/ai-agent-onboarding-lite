import json
import random
import string
import asyncio
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from typing import Any, Optional


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data):
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@lru_cache(maxsize=128)
def read_json_cached(path: Path, default=None) -> Any:
    """Optimized JSON reading with LRU caching for frequently accessed files."""
    path_str = str(path.resolve())  # Cache key based on resolved path
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


async def read_json_async(path: Path, default=None) -> Any:
    """Async version of JSON reading for concurrent file operations."""
    if not path.exists():
        return default
    try:
        # Use asyncio.to_thread for the blocking I/O operation
        content = await asyncio.to_thread(path.read_text, encoding="utf-8")
        return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return default


def read_json(path: Path, default=None):
    """Backward-compatible JSON reading - now uses optimized cached version."""
    return read_json_cached(path, default)


async def read_multiple_json(paths: list[Path], default=None) -> list[Any]:
    """Read multiple JSON files concurrently using asyncio."""
    tasks = [read_json_async(path, default) for path in paths]
    return await asyncio.gather(*tasks, return_exceptions=True)


def read_multiple_json_sync(paths: list[Path], default=None) -> list[Any]:
    """Synchronous wrapper for concurrent JSON reading."""
    try:
        # Try to run in an existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, fall back to sequential reading
            return [read_json_cached(path, default) for path in paths]
        else:
            return loop.run_until_complete(read_multiple_json(paths, default))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(read_multiple_json(paths, default))


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def dumps_json(data) -> str:
    """Safe JSON serializer used by CLI output paths.

    Falls back to default=str for objects that aren't natively serializable.
    """
    try:
        return json.dumps(data, ensure_ascii=False)
    except TypeError:
        return json.dumps(data, ensure_ascii=False, default=str)


def random_string(length: int = 8) -> str:
    """Generate a random string of specified length."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
