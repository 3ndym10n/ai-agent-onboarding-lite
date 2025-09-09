import json
import random
import string
from datetime import datetime
from pathlib import Path


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data):
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


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
