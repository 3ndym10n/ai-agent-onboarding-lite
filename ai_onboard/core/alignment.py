from pathlib import Path
import json

from . import utils


def open_checkpoint(root: Path, name: str) -> None:
    log = root / ".ai_onboard" / "decision_log.jsonl"
    utils.ensure_dir(log.parent)
    with open(log, "a", encoding="utf-8") as f:
        f.write(
            f'{{"ts":"{utils.now_iso()}","decision":"OPEN","subject":"{name}"}}\n'
        )


def record_decision(root: Path, decision: str, subject: str, approved: bool, note: str) -> None:
    """Record a decision to the JSON lines log.

    Each decision is stored as a single JSON object per line. ``json.dump`` is
    used so that notes are escaped safely.
    """
    log = root / ".ai_onboard" / "decision_log.jsonl"
    utils.ensure_dir(log.parent)
    entry = {
        "ts": utils.now_iso(),
        "decision": decision,
        "subject": subject,
        "approved": approved,
        "note": note,
    }
    with open(log, "a", encoding="utf-8") as f:
        json.dump(entry, f)
        f.write("\n")


def require_alignment(root: Path, checkpoint: str) -> None:
    """Ensure that ``checkpoint`` has an approved ALIGN decision.

    The decision log stores JSON objects, one per line. Each line is parsed to
    check for a matching approved ALIGN entry. Malformed lines are skipped.
    """
    log = root / ".ai_onboard" / "decision_log.jsonl"
    if not log.exists():
        raise SystemExit(f"Alignment required: {checkpoint}")

    ok = False
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            entry.get("decision") == "ALIGN"
            and entry.get("subject") == checkpoint
            and entry.get("approved") is True
        ):
            ok = True
            break

    if not ok:
        raise SystemExit(f"Alignment approval missing for {checkpoint}")


def require_state(root: Path, needed: str) -> None:
    from . import state

    state.require_gate(root, needed)


# --- Intelligent Alignment Preview (non-invasive) ---

def _load_policy(root: Path) -> dict:
    """Load IAS policy YAML if available; otherwise return defaults.

    The function gracefully handles environments without PyYAML installed.
    """
    policy_path = root / "ai_onboard" / "policies" / "alignment_rules.yaml"
    defaults = {
        "confidence": {
            "proceed": 0.90,
            "quick_confirm": 0.75,
            "clarify": 0.0,
            "weights": {
                "vision_completeness": 0.25,
                "prior_confirmations": 0.25,
                "benchmark_fit": 0.20,
                "ambiguity_inverse": 0.20,
                "change_impact_inverse": 0.10,
            },
        },
        "outputs": {"report_path": ".ai_onboard/alignment_report.json"},
    }
    if not policy_path.exists():
        return defaults
    try:
        import yaml  # type: ignore

        with open(policy_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        # Merge shallowly with defaults
        out = defaults.copy()
        out.update({k: v for k, v in data.items() if v is not None})
        return out
    except Exception:
        # Fall back to defaults if YAML parsing not available
        return defaults


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default


def _score_between(z: float) -> float:
    return 0.0 if z < 0 else 1.0 if z > 1 else z


def _compute_confidence(root: Path, policy: dict) -> dict:
    """Compute a lightweight confidence from available artifacts.

    Heuristics (v1):
    - vision_completeness: presence of charter and top_outcomes
    - prior_confirmations: ALIGN approvals in decision_log
    - benchmark_fit: coarse heuristic using presence of tests/docs
    - ambiguity_inverse: inverse of detected ambiguities (0 if many)
    - change_impact_inverse: neutral 0.5 (unknown until diff known)
    """
    weights = policy.get("confidence", {}).get("weights", {})

    charter_path = root / ".ai_onboard" / "charter.json"
    charter_data = _read_json(charter_path, default={}) or {}
    top_outcomes = (charter_data.get("top_outcomes") or []) if isinstance(charter_data, dict) else []
    vision_completeness = 1.0 if top_outcomes else (0.6 if charter_path.exists() else 0.0)

    # Prior confirmations
    log = root / ".ai_onboard" / "decision_log.jsonl"
    approved = 0
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("decision") == "ALIGN" and entry.get("approved") is True:
                approved += 1
    prior_confirmations = 1.0 if approved > 0 else 0.0

    # Benchmark fit: very coarse heuristic for now
    has_tests = (root / "tests").exists()
    has_docs = (root / "docs").exists()
    benchmark_fit = 1.0 if (has_tests and has_docs) else 0.6 if (has_tests or has_docs) else 0.4

    # Ambiguity detection (basic)
    ambiguities = []
    if not top_outcomes:
        ambiguities.append("missing_top_outcomes")
    plan_exists = (root / ".ai_onboard" / "plan.json").exists()
    if plan_exists and not charter_path.exists():
        ambiguities.append("plan_without_charter")
    ambiguity_score = 0.0 if len(ambiguities) >= 2 else (0.5 if ambiguities else 1.0)
    ambiguity_inverse = ambiguity_score

    # Change impact is unknown in preview; keep neutral
    change_impact_inverse = 0.5

    # Weighted sum
    vc_w = float(weights.get("vision_completeness", 0.25))
    pc_w = float(weights.get("prior_confirmations", 0.25))
    bf_w = float(weights.get("benchmark_fit", 0.20))
    ai_w = float(weights.get("ambiguity_inverse", 0.20))
    ci_w = float(weights.get("change_impact_inverse", 0.10))

    confidence = (
        vision_completeness * vc_w
        + prior_confirmations * pc_w
        + benchmark_fit * bf_w
        + ambiguity_inverse * ai_w
        + change_impact_inverse * ci_w
    )
    confidence = _score_between(confidence)

    components = {
        "vision_completeness": round(vision_completeness, 3),
        "prior_confirmations": round(prior_confirmations, 3),
        "benchmark_fit": round(benchmark_fit, 3),
        "ambiguity_inverse": round(ambiguity_inverse, 3),
        "change_impact_inverse": round(change_impact_inverse, 3),
    }
    return {"confidence": round(confidence, 3), "components": components, "ambiguities": ambiguities}


def preview(root: Path) -> dict:
    """Compute a read-only alignment preview and write a JSON report.

    Returns a dict with confidence, decision (proceed|quick_confirm|clarify),
    components, and path of the written report.
    """
    policy = _load_policy(root)
    score = _compute_confidence(root, policy)

    thresholds = policy.get("confidence", {})
    proceed_t = float(thresholds.get("proceed", 0.90))
    qc_t = float(thresholds.get("quick_confirm", 0.75))

    c = float(score.get("confidence", 0.0))
    if c >= proceed_t:
        decision = "proceed"
    elif c >= qc_t:
        decision = "quick_confirm"
    else:
        decision = "clarify"

    report = {
        "ts": utils.now_iso(),
        "confidence": c,
        "decision": decision,
        "components": score.get("components", {}),
        "ambiguities": score.get("ambiguities", []),
        "policy": {"thresholds": {"proceed": proceed_t, "quick_confirm": qc_t}},
    }

    report_rel = policy.get("outputs", {}).get("report_path", ".ai_onboard/alignment_report.json")
    report_path = root / report_rel
    utils.write_json(report_path, report)
    return {"report_path": str(report_path), **report}
