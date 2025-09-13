from pathlib import Path

from . import utils, versioning


def write_report(root: Path, res: dict) -> None:
    out = ["# AI Onboard Report", ""]
    summary = (res or {}).get("summary", {})
    if summary:
        out.append(f"Overall: {'PASS' if summary.get('pass') else 'FAIL'}")
        out.append("")
    for r in (res or {}).get("results", []):
        comp = r.get("component", "unknown")
        score = r.get("score")
        score_s = f"{score:.2f}" if isinstance(score, (int, float)) else "n / a"
        out.append(f"## Component: {comp} — score {score_s}")
        issues = r.get("issues", []) or []
        if not issues:
            out.append("- No issues")
        for i in issues:
            sev = (i.get("severity") or "").upper()
            rule = i.get("rule_id", "?")
            msg = i.get("message", "")
            where = f" ({i.get('file')})" if i.get("file") else ""
            out.append(f"- [{sev}] {rule}: {msg}{where}")
        out.append("")
    utils.ensure_dir(root / ".ai_onboard")
    content = "\n".join(out)
    # canonical
    (root / ".ai_onboard" / "report.md").write_text(content, encoding="utf - 8")
    # versioned copy
    v = versioning.get_version(root)
    (root / ".ai_onboard" / f"report_v{v}.md").write_text(content, encoding="utf - 8")
