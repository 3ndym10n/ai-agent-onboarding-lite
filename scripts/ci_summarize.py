#!/usr/bin/env python3
# mypy: ignore-errors
"""
Summarize recent CI logs fetched into `.ai_onboard/logs/` into a single JSON report.

- Scans for job logs like `ci__quality.log`, `ci__test__3_9_.log`, etc.
- Extracts key failure indicators and last lines.
- Writes `.ai_onboard/logs/summary.json` with a compact overview.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

LOG_DIR = Path(".ai_onboard/logs")
SUMMARY_PATH = LOG_DIR / "summary.json"

ERROR_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"would reformat"),
    re.compile(r"##\[error\]", re.I),
    re.compile(r"Traceback"),
    re.compile(r"AssertionError"),
    re.compile(r"TypeError"),
    re.compile(r"E\d{3}\b"),  # flake8 codes
]


def _read_tail_lines(path: Path, max_lines: int = 200) -> List[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[-max_lines:]
    except Exception:  # noqa: BLE001 - defensive
        return []


def _extract_hits(lines: List[str]) -> List[str]:
    hits: List[str] = []
    for line in lines:
        for pat in ERROR_PATTERNS:
            if pat.search(line):
                hits.append(line.strip())
                break
    # Deduplicate, preserve order
    seen: set[str] = set()
    unique = []
    for h in hits:
        if h not in seen:
            unique.append(h)
            seen.add(h)
    return unique[:30]


def summarize() -> Dict[str, object]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    report: Dict[str, object] = {"jobs": {}, "notes": []}

    for log_file in sorted(LOG_DIR.glob("ci__*.log")):
        job_name = log_file.stem.replace("ci__", "").replace("_", " ").strip()
        tail = _read_tail_lines(log_file)
        hits = _extract_hits(tail)
        report["jobs"][job_name] = {
            "path": str(log_file.as_posix()),
            "hits": hits,
            "tail": tail[-20:],
        }

    # Add raw events if available
    events_path = LOG_DIR / "events.jsonl"
    if events_path.exists():
        try:
            # Grab only the last few
            events_lines = events_path.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()[-50:]
            report["events_tail"] = events_lines
        except Exception:  # noqa: BLE001
            pass

    return report


def main() -> None:
    report = summarize()
    SUMMARY_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
