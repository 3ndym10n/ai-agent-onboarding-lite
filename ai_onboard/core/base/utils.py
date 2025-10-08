"""
Core utility functions for AI Onboard.

Provides common functionality used throughout the system including:
- File system operations
- JSON handling with caching
- Random ID generation
- Date/time utilities
- Error handling classes
- Plugin registry
- Profiling and telemetry
- Issue tracking
- Methodology selection
- Intent checking
"""

import asyncio
import json
import random
import string
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Protocol, Tuple


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def generate_id(length: int = 8) -> str:
    """Generate a random alphanumeric ID of specified length."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def write_json(path: Path, data):
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf - 8")
    # Invalidate cache entry to ensure subsequent reads get fresh data
    cache_key = str(path.resolve())
    if cache_key in _json_cache:
        del _json_cache[cache_key]
    if cache_key in _json_cache_access:
        del _json_cache_access[cache_key]


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
        content = json.loads(path.read_text(encoding="utf - 8"))
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
        # Use asyncio.to_thread (Python 3.9+) with fallback for Python 3.8
        if hasattr(asyncio, 'to_thread'):
            content = await asyncio.to_thread(path.read_text, encoding="utf - 8")
        else:
            # Fallback for Python 3.8: use run_in_executor
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, path.read_text, "utf - 8")
        return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return default


def read_json(path: Path, default=None):
    """Backward - compatible JSON reading - now uses optimized cached version."""
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
    """Return ISO 8601 timestamp with Z suffix (UTC)."""
    # Replace +00:00 with Z to avoid mixed-offset format (e.g., +00:00Z)
    return datetime.now(timezone.utc).isoformat().replace('+00:00', '') + "Z"


def dumps_json(data) -> str:
    """Safe JSON serializer used by CLI output paths.

    Falls back to default = str for objects that aren't natively serializable.
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
    with open(path, "a", encoding="utf - 8") as f:
        f.write(json_line)


def create_timestamped_backup(source: Path, backup_dir: Path) -> Path:
    """Create a timestamped backup of a file."""
    ensure_dir(backup_dir)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{source.stem}_{timestamp}{source.suffix}"
    backup_path.write_text(source.read_text(encoding="utf - 8"), encoding="utf - 8")
    return backup_path


def restore_backup(backup_path: Path, target_path: Path) -> bool:
    """Restore a file from a backup path."""
    if not backup_path.exists():
        return False
    ensure_dir(target_path.parent)
    target_path.write_text(
        backup_path.read_text(encoding="utf - 8"), encoding="utf - 8"
    )
    return True


# =============================================================================
# ERROR HANDLING CLASSES (consolidated from errors.py)
# =============================================================================


class AiOnboardError(Exception):
    """Base exception for AI Onboard system."""


class PolicyError(AiOnboardError):
    """Exception raised when policy validation fails."""


class GuardBlocked(AiOnboardError):
    """Exception raised when a guard blocks an operation."""


def err(code: str, msg: str, **k):
    """Create an error response dictionary."""
    out = {"ok": False, "code": code, "message": msg}
    out.update(k or {})
    return out


def ok(**k):
    """Create a success response dictionary."""
    out = {"ok": True}
    out.update(k or {})
    return out


# =============================================================================
# ISSUE TRACKING (consolidated from issue.py)
# =============================================================================

Severity = Literal["error", "warn", "info"]


@dataclass
class Issue:
    """Represents an issue found during validation or analysis."""

    rule_id: str
    severity: Severity
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    confidence: float = 0.0
    remediation: Optional[str] = None


# =============================================================================
# PLUGIN REGISTRY (consolidated from registry.py)
# =============================================================================


class CheckPlugin(Protocol):
    """Protocol for check plugins."""

    name: str

    def run(self, paths: List[str], ctx: Dict[str, Any]) -> List[Issue]:
        """Run the check plugin."""
        ...


REGISTRY: Dict[Tuple[str, str], List[CheckPlugin]] = {}


def register(component_type: str, language: str, plugin: CheckPlugin):
    """Register a check plugin."""
    REGISTRY.setdefault((component_type, language), []).append(plugin)


# =============================================================================
# PROFILING UTILITIES (consolidated from profiler.py)
# =============================================================================


@contextmanager
def timer():
    """Context manager for timing operations."""
    t0 = time.time()
    yield lambda: time.time() - t0


# =============================================================================
# METHODOLOGY SELECTION (consolidated from methodology.py)
# =============================================================================


def pick_methodology(ch: dict) -> dict:
    """Pick appropriate methodology based on charter parameters."""
    team = ch.get("team_size", 3)
    horizon = ch.get("delivery_horizon_days", 30)
    pref = ch.get("preferred_methodology", "auto")

    if pref != "auto":
        chosen = pref
    elif team <= 4 and horizon < 21:
        chosen = "kanban"
    elif horizon >= 21:
        chosen = "scrum"
    else:
        chosen = "hybrid"

    return {
        "chosen": chosen,
        "rationale": f"team={team}, horizon={horizon}, pref={pref}",
    }


# =============================================================================
# AGENT TELEMETRY (consolidated from agent_telemetry.py)
# =============================================================================


def record_agent_event(root: Path, rec: Dict[str, Any]) -> None:
    """Append a single cross-agent record to agents.jsonl. Best-effort."""
    path = root / ".ai_onboard" / "agents.jsonl"
    ensure_dir(path.parent)
    out = {
        "ts": now_iso(),
    }
    out.update(rec or {})
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(out, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass  # Best effort - don't fail if telemetry fails


# =============================================================================
# INTENT CHECKING (consolidated from intent_checks.py)
# =============================================================================


def applicable_rules(
    root: Path, manifest: Dict[str, Any], target_path: str, change: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Get applicable rules for a given change."""
    # Import here to avoid circular imports
    from ..utilities import meta_policy

    rules = meta_policy.rules_summary(manifest)
    # Optionally tailor by target
    for r in rules:
        r["target"] = target_path
    return rules


def propose_intent_decision(
    root: Path, manifest: Dict[str, Any], diff: Dict[str, Any]
) -> Dict[str, Any]:
    """Propose a decision based on intent analysis."""
    # Import here to avoid circular imports
    from ..utilities import meta_policy

    ff = manifest.get("features") or {}
    if ff.get("intent_checks", True) is False:
        return {
            "decision": "allow",
            "reasons": [{"rule": "feature_flag", "detail": "intent_checks disabled"}],
        }
    return meta_policy.evaluate(manifest, diff)
