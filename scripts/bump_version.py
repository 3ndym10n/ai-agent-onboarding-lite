import pathlib
import re
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts / bump_version.py <x.y.z>")
        return 2
    new = sys.argv[1].strip()
    root = pathlib.Path(__file__).resolve().parents[1]

    # pyproject.toml
    pp_path = root / "pyproject.toml"
    text = pp_path.read_text(encoding="utf - 8")
    text = re.sub(
        r'version\s*=\s*"[0 - 9]+\.[0 - 9]+\.[0 - 9]+"', f'version = "{new}"', text
    )
    pp_path.write_text(text, encoding="utf - 8")

    # ai_onboard / __init__.py
    (root / "ai_onboard" / "__init__.py").write_text(
        f'__version__ = "{new}"\n', encoding="utf - 8"
    )

    # ai_onboard / VERSION.txt
    (root / "ai_onboard" / "VERSION.txt").write_text(new + "\n", encoding="utf - 8")

    print(new)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
