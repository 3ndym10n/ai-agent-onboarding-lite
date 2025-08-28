from pathlib import Path
from . import utils

def parse_budget(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("m"): return int(s[:-1]) * 60
    if s.endswith("s"): return int(s[:-1])
    return int(s)

def quick_optimize(root: Path, budget: str="300s") -> None:
    trials = root / ".ai_onboard" / "optimizer_trials.jsonl"
    utils.ensure_dir(trials.parent)
    with open(trials, "a", encoding="utf-8") as f:
        f.write(f'{{"ts":"{utils.now_iso()}","trial":"ordering/parallel","budget_s":{parse_budget(budget)},"result":"stub"}}\n')
    print("Optimizer ran a quick (stub) trial. (Hooks are ready for deeper logic.)")

def nudge_from_metrics(root: Path) -> None:
    # Read metrics and nudge parameters (stubbed for now)
    print("Kaizen: reviewed metrics and kept current schedule (stub).")
