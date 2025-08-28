import json
from pathlib import Path
def ensure_dir(path: Path): path.mkdir(parents=True, exist_ok=True)
def write_json(path: Path, data): ensure_dir(path.parent); path.write_text(json.dumps(data, indent=2))
def read_json(path: Path, default=None): return json.loads(path.read_text()) if path.exists() else default
