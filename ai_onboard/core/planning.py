from pathlib import Path
from . import utils

def build(root: Path) -> dict:
    ch = utils.read_json(root / ".ai_onboard" / "charter.json", default=None)
    if not ch:
        raise SystemExit("Missing charter. Run: python -m ai_onboard charter")
    wbs = [
      {"id":"C1","name":"Core setup","deps":[]},
      {"id":"C2","name":"Discovery/manifest","deps":["C1"]},
      {"id":"C3","name":"Plugin surface","deps":["C1"]},
      {"id":"C4","name":"Language adapters (min)","deps":["C3"]},
      {"id":"C5","name":"CLI+docs","deps":["C1","C3"]}
    ]
    plan = {
      "methodology": ch.get("methodology",{}),
      "wbs": wbs,
      "milestones": [{"name":"Charter Gate"},{"name":"Plan Gate"},{"name":"Alignment Gate"}],
      "risks":[{"id":"R1","desc":"Over-generalization","mitigation":"policy overlays","severity":"M"}],
      "resources":{"roles":["owner","dev","reviewer"],"limits":{"allowExec": False}},
      "policy_overlays": [],
      "reporting":{"cadence":"weekly","artifacts":["progress.md","metrics.json"]}
    }
    utils.write_json(root / ".ai_onboard" / "plan.json", plan)
    return plan
