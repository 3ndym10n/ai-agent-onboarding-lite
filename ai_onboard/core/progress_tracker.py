from pathlib import Path
from . import utils, versioning

def write_report(root: Path, res: dict) -> None:
    out = ["# AI Onboard Report", ""]
    for r in res["results"]:
        out.append(f"## Component: {r['component']} — score {r['score']:.2f}")
        if not r["issues"]:
            out.append("- No issues")
        for i in r["issues"]:
            where = f" ({i['file']})" if i.get("file") else ""
            out.append(f"- [{i['severity'].upper()}] {i['rule_id']}: {i['message']}{where}")
        out.append("")
    utils.ensure_dir(root / ".ai_onboard")
    content = "\n".join(out)
    # canonical
    (root / ".ai_onboard" / "report.md").write_text(content, encoding="utf-8")
    # versioned copy
    v = versioning.get_version(root)
    (root / ".ai_onboard" / f"report_v{v}.md").write_text(content, encoding="utf-8")
