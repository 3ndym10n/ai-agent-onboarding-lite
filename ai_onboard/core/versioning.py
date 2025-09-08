from pathlib import Path


def version_file(root: Path) -> Path:
    # Keep in sync with setuptools_scm config pointing at VERSION.txt
    return root / "ai_onboard" / "VERSION.txt"


def get_version(root: Path) -> str:
    vf = version_file(root)
    if not vf.exists():
        return "0.1.0"
    return vf.read_text(encoding="utf-8").strip() or "0.1.0"


def set_version(root: Path, v: str) -> None:
    vf = version_file(root)
    vf.write_text(v.strip() + "\n", encoding="utf-8")


def bump(version: str, kind: str) -> str:
    major, minor, patch = [int(x) for x in version.split(".")]
    if kind == "major":
        return f"{major+1}.0.0"
    if kind == "minor":
        return f"{major}.{minor+1}.0"
    return f"{major}.{minor}.{patch+1}"
