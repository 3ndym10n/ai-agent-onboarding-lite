from pathlib import Path
from typing import Any, Dict, List

from . import (
    cache,
    error_resolver,
    optimizer_state,
    policy_engine,
    profiler,
    registry,
    scheduler,
    schema_validate,
    telemetry,
    utils,
)
from .issue import Issue


def run(root: Path) -> Dict[str, Any]:
    manifest = utils.read_json(root / "ai_onboard.json", default = None)
    if not manifest:
        raise SystemExit("Missing ai_onboard.json. Run: python -m ai_onboard analyze")
    policy = policy_engine.load(root)
    # Validate effective policy against minimal schema (non - invasive)
    try:
        schema_validate.validate_policy(policy)
        telemetry.log_event(
            "policy_validation", decision="ok", rules = len(policy.get("rules", []) or [])
        )
    except Exception as e:
        telemetry.log_event("policy_validation", decision="fail", error = str(e))
        raise SystemExit(f"Policy validation failed: {e}")
    components = manifest.get("components", [])
    idx = cache.load(root)
    changed = cache.changed_files(root, idx)

    results = []
    all_pass = True

    for comp in components:
        key = (comp.get("type", ""), comp.get("language", ""))
        plugins = registry.REGISTRY.get(key, [])
        comp_files = comp.get("paths", ["."])
        ctx = {"root": str(root), "comp": comp, "policy": policy}

        # Create pseudo - rule list from plugin names for scheduler ordering
        rules = [{"id": getattr(p, "name", p.__class__.__name__)} for p in plugins]
        # Load optimizer state to inform scheduling (fault_yield / avg_time)
        opt_state = optimizer_state.load(root)
        # Build dynamic history / profiler views from state
        hist = {}
        prof = {}
        for r in rules:
            rid = r["id"]
            hist[rid] = {
                "fault_yield": optimizer_state.fault_yield(opt_state, rid),
                "passes_in_row": optimizer_state.passes_in_row(opt_state, rid),
            }
            prof[rid] = {"p50_time": optimizer_state.avg_time(opt_state, rid)}
        ordered = scheduler.order_rules(rules, hist, prof)

        issues: List[Issue] = []
        for r in ordered:
            impacted = cache.rule_impacted(idx, r["id"], changed)
            if scheduler.should_skip(r, hist, impacted):
                continue
            plugin = next(
                (p for p in plugins if getattr(p, "name", "") == r["id"]), None
            )
            if not plugin:
                continue
            try:
                with profiler.timer() as elapsed:
                    before_count = len(issues)
                    issues.extend(plugin.run(comp_files, ctx))
                    duration_s = elapsed()
                    found = len(issues) - before_count
                    # Update optimizer state per rule
                    optimizer_state.update_rule_stats(
                        opt_state, r["id"], duration_s, found
                    )
            except Exception as e:
                # Convert runtime exceptions into issues, and fingerprint them
                msg = f"Plugin crash: {e}"
                fp = error_resolver.fingerprint(msg, r["id"])
                error_resolver.record_kb(root, fp, "plugin_run", "crash")
                issues.append(error_resolver.issue_from_fp(fp, r["id"], msg))

        # Persist updated optimizer state after processing this component
        optimizer_state.save(root, opt_state)

        # Post - process issues: fingerprint & create ask - cards if repeated
        for i in list(issues):
            fp = error_resolver.fingerprint(i.message, i.file or comp.get("name", ""))
            error_resolver.touch_fp(root, fp)
            suggestion = error_resolver.suggest_move_from_rule(i.rule_id, i.message)
            if error_resolver.should_ask(root, fp):
                error_resolver.ask_card(
                    root, suggestion["question"], suggestion["options"]
                )

        score = _score(policy, issues)
        all_pass = all_pass and (
            score >= policy.get("scoring", {}).get("pass_threshold", 0.7)
        )
        results.append(
            {
                "component": comp["name"],
                "issues": [i.__dict__ for i in issues],
                "score": score,
            }
        )

    cache.save(root, idx)
    return {"results": results, "summary": {"pass": all_pass}}


def _score(policy: dict, issues: List) -> float:
    weights = policy.get("scoring", {}).get(
        "weights", {"error": 1.0, "warn": 0.4, "info": 0.1}
    )
    total = 1.0
    penalty = 0.0
    for i in issues:
        penalty += weights.get(i.severity, 0.0) * (i.confidence or 1.0) * 0.1
    return max(0.0, min(1.0, total - penalty))
