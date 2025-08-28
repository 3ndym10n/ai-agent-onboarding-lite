#!/usr/bin/env python3
"""
Kaizen Improvement Orchestrator for VectorFlow Onboarding

- Runs enhanced validation cycles
- Computes reward signals (issue reduction, validation rate)
- Updates IntelligentErrorResolver bandit with success/failure
- Optionally tunes validation policy slightly for continuous improvement
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from enhanced_progress_tracker import EnhancedProgressTracker
from INTELLIGENT_ERROR_RESOLVER import IntelligentErrorResolver


class KaizenOrchestrator:
    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.onboarding_dir = self.project_root / "onboarding"
        self.metrics_file = self.onboarding_dir / "kaizen_metrics.json"
        self.policy_file = self.onboarding_dir / "validation_policy.json"
        self.tracker = EnhancedProgressTracker(project_root)
        self.resolver = IntelligentErrorResolver(self.project_root)
        self.metrics: Dict[str, Any] = self._load_metrics()

    def _load_metrics(self) -> Dict[str, Any]:
        if self.metrics_file.exists():
            try:
                return json.loads(self.metrics_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "history": [],
            "last_total_issues": None,
            "last_validation_rate": None,
        }

    def _save_metrics(self):
        self.metrics_file.write_text(json.dumps(self.metrics, indent=2), encoding="utf-8")

    def _flatten_issue_count(self, results: Dict[str, Any]) -> int:
        total = 0
        for category in ("infrastructure", "analytics_modules", "critical_missing"):
            for _name, details in results.get(category, {}).items():
                total += len(details.get("issues", []))
        return total

    def _validation_rate(self, results: Dict[str, Any]) -> float:
        return float(results.get("summary", {}).get("validation_rate", 0.0))

    def _adjust_policy(self, improvement: float):
        try:
            if not self.policy_file.is_file():
                return
            policy = json.loads(self.policy_file.read_text(encoding="utf-8"))
            # Small, bounded adjustments based on improvement signal
            # If improvement positive -> relax slightly; if negative -> tighten slightly
            def clamp(val: float, lo: float, hi: float) -> float:
                return max(lo, min(hi, val))

            delta = 1.0 if improvement < 0 else -1.0
            # UI sensitivity
            ui_pen = float(policy.get("ui", {}).get("issue_penalty_pct", 10))
            policy["ui"]["issue_penalty_pct"] = clamp(ui_pen + delta, 5, 20)
            # Analytics sensitivity
            an_pen = float(policy.get("analytics", {}).get("issue_penalty_pct", 8))
            policy["analytics"]["issue_penalty_pct"] = clamp(an_pen + delta, 4, 16)
            # Data sensitivity
            data_pen = float(policy.get("data", {}).get("issue_penalty_pct", 8))
            policy["data"]["issue_penalty_pct"] = clamp(data_pen + delta, 4, 16)

            self.policy_file.write_text(json.dumps(policy, indent=2), encoding="utf-8")
        except Exception:
            # Non-fatal: policy tuning is optional
            pass

    def run_cycle(self) -> Dict[str, Any]:
        # Run enhanced validation and collect metrics
        results = self.tracker.scan_with_validation()
        total_issues = self._flatten_issue_count(results)
        validation_rate = self._validation_rate(results)

        # Compute reward relative to last run
        last_issues = self.metrics.get("last_total_issues")
        last_rate = self.metrics.get("last_validation_rate")

        reward = 0.0
        if isinstance(last_issues, int):
            # Reward = reduction in issues + improvement in validation rate
            reward += float(last_issues - total_issues)
        if isinstance(last_rate, (int, float)):
            reward += (validation_rate - float(last_rate)) * 0.5

        # Update resolver bandit with success/failure signal
        success = reward > 0
        self.resolver.log_resolution(
            task_name="kaizen",
            action="policy_tuning",
            target="validation",
            resolution="general escalation: adjusted policy weights",
            success=success,
        )

        # Optionally adjust policy slightly for continuous improvement
        self._adjust_policy(reward)

        # Save metrics history
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_issues": total_issues,
            "validation_rate": validation_rate,
            "reward": reward,
            "success": success,
        }
        self.metrics["history"].append(snapshot)
        self.metrics["last_total_issues"] = total_issues
        self.metrics["last_validation_rate"] = validation_rate
        self._save_metrics()
        return snapshot


def main():
    import sys
    root = ".."
    if len(sys.argv) > 1:
        root = sys.argv[1]
    orchestrator = KaizenOrchestrator(root)
    snapshot = orchestrator.run_cycle()
    print("Kaizen cycle complete:")
    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
