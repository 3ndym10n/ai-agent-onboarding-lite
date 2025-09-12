import asyncio
import json
import random
import string
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def generate_id(length: int = 8) -> str:
    """Generate a random alphanumeric ID of specified length."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def write_json(path: Path, data):
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# Global cache for JSON files
_json_cache: Dict[str, Any] = {}
_json_cache_access: Dict[str, float] = {}
_JSON_CACHE_MAX_SIZE = 128


def _cleanup_json_cache():
    """Remove oldest entries if cache is too large."""
    if len(_json_cache) > _JSON_CACHE_MAX_SIZE:
        # Remove oldest entries
        oldest_keys = sorted(_json_cache_access.items(), key=lambda x: x[1])[
            : len(_json_cache) - _JSON_CACHE_MAX_SIZE
        ]
        for key, _ in oldest_keys:
            del _json_cache[key]
            del _json_cache_access[key]


def read_json_cached(path: Path, default=None) -> Any:
    """Optimized JSON reading with LRU caching for frequently accessed files."""
    cache_key = str(path.resolve())

    # Check cache first
    if cache_key in _json_cache:
        _json_cache_access[cache_key] = time.time()  # Update access time
        return _json_cache[cache_key]

    if not path.exists():
        return default

    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        # Cache the result
        _json_cache[cache_key] = content
        _json_cache_access[cache_key] = time.time()
        _cleanup_json_cache()
        return content
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


async def read_multiple_json(paths: List[Path], default=None) -> List[Any]:
    """Read multiple JSON files concurrently using asyncio."""
    tasks = [read_json_async(path, default) for path in paths]
    return await asyncio.gather(*tasks, return_exceptions=True)


def read_multiple_json_sync(paths: List[Path], default=None) -> List[Any]:
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


def append_jsonl(path: Path, data: Dict[str, Any]):
    """Append a JSON object to a JSONL file."""
    ensure_dir(path.parent)

    # Convert data to JSON string
    json_line = json.dumps(data, ensure_ascii=False, default=str) + "\n"

    # Append to file
    with open(path, "a", encoding="utf-8") as f:
        f.write(json_line)
