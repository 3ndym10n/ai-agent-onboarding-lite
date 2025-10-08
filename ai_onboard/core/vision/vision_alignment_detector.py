"""
Advanced vision alignment detector for AI Onboard.

Evaluates proposed changes against the project's charter, plan, WBS, and
constraints to determine whether the work stays within scope.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol, Tuple

from ..base import utils

AlignmentDecision = str  # Literal["proceed", "review", "block"] (py38 compat)


@dataclass
class AlignmentMatch:
    """A single match between the suggestion and a reference artifact."""

    label: str
    similarity: float
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlignmentAssessment:
    """Overall assessment returned by the detector."""

    decision: AlignmentDecision
    score: float
    reasons: List[str]
    constraint_hits: List[str]
    matches: Dict[str, List[AlignmentMatch]]
    phase_alignment: Dict[str, Optional[str]]
    components: Dict[str, float]


class SimilarityScorer(Protocol):
    """Protocol for pluggable similarity scorers."""

    def score(self, lhs: str, rhs: str) -> float:
        ...


class TfCosineSimilarityScorer:
    """
    Simple term-frequency cosine similarity scorer.

    Uses whitespace / punctuation tokenization with lowercase normalization.
    """

    TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

    def _vectorize(self, text: str) -> Counter:
        tokens = self.TOKEN_PATTERN.findall(text.lower())
        return Counter(tokens)

    def score(self, lhs: str, rhs: str) -> float:
        vec1 = self._vectorize(lhs)
        vec2 = self._vectorize(rhs)
        if not vec1 or not vec2:
            return 0.0
        intersection = set(vec1) & set(vec2)
        numerator = sum(vec1[token] * vec2[token] for token in intersection)
        if numerator == 0:
            return 0.0
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return numerator / (norm1 * norm2)


@dataclass
class _Candidate:
    label: str
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)


class VisionAlignmentDetector:
    """
    Evaluate natural language suggestions against project vision & constraints.
    """

    DEFAULT_WEIGHTS = {"alignment": 0.65, "phase": 0.25, "complexity": 0.1}
    DEFAULT_THRESHOLDS = {"proceed": 0.6, "review": 0.4}

    COMPLEXITY_INDICATORS = {
        "advanced": [
            "authentication",
            "authorization",
            "dashboard",
            "analytics",
            "machine learning",
            "microservice",
            "kubernetes",
            "api",
            "graphql",
            "multitenant",
            "realtime",
            "streaming",
            "message queue",
            "distributed",
        ]
    }

    def __init__(
        self,
        project_root: Path,
        *,
        scorer: Optional[SimilarityScorer] = None,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.scorer: SimilarityScorer = scorer or TfCosineSimilarityScorer()
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()

        self._load_context()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def assess(self, suggestion: str, *, metadata: Optional[Dict[str, str]] = None) -> AlignmentAssessment:
        """Return an alignment assessment for the supplied suggestion."""
        text = suggestion.strip()
        metadata = metadata or {}
        reasons: List[str] = []
        matches: Dict[str, List[AlignmentMatch]] = {}
        constraint_hits = self._check_constraints(text)

        # If hard constraints violated, short-circuit.
        if constraint_hits:
            reasons.append("Suggestion violates project guardrails.")
            components = {"alignment": 0.0, "phase": 0.0, "complexity": 0.0}
            assessment = AlignmentAssessment(
                decision="block",
                score=0.1,
                reasons=reasons + constraint_hits,
                constraint_hits=constraint_hits,
                matches={},
                phase_alignment={"current": self.current_phase, "match": None},
                components=components,
            )
            return assessment

        charter_matches = self._score_candidates(text, self._charter_candidates, top_k=3)
        if charter_matches:
            reasons.append(
                f"Strongest objective match: '{charter_matches[0].label}' (similarity {charter_matches[0].similarity:.2f})"
            )
        matches["charter"] = charter_matches

        task_matches = self._score_candidates(text, self._wbs_candidates, top_k=3)
        best_task: Optional[AlignmentMatch] = task_matches[0] if task_matches else None
        if best_task:
            reasons.append(
                f"Closest WBS task: '{best_task.label}' (phase {best_task.metadata.get('phase','?')}, similarity {best_task.similarity:.2f})"
            )
        matches["wbs"] = task_matches

        alignment_score = 0.0
        if charter_matches:
            alignment_score = max(alignment_score, charter_matches[0].similarity)
        if best_task:
            alignment_score = max(alignment_score, best_task.similarity)

        # Light heuristic boost when suggestion shares key tokens with the best task label
        if best_task:
            label_tokens = set(self._tokenize(best_task.label))
            sugg_tokens = set(self._tokenize(text))
            overlap = label_tokens & sugg_tokens
            if overlap:
                # Slightly increase the bonus to better recognize
                # in-scope enhancements without lowering global thresholds
                alignment_score = min(1.0, alignment_score + 0.15)

        phase_component, phase_reason, matched_phase = self._phase_component(best_task)
        if phase_reason:
            reasons.append(phase_reason)

        complexity_component, complexity_reason = self._complexity_component(text)
        if complexity_reason:
            reasons.append(complexity_reason)

        components = {
            "alignment": round(alignment_score, 3),
            "phase": round(phase_component, 3),
            "complexity": round(complexity_component, 3),
        }

        score = (
            self.weights.get("alignment", 0.6) * alignment_score
            + self.weights.get("phase", 0.2) * phase_component
            + self.weights.get("complexity", 0.2) * complexity_component
        )
        score = max(0.0, min(1.0, score))

        # Practical adjustments:
        # - If phase is perfectly aligned and alignment is decent, grant a small bonus
        if phase_component >= 0.99 and alignment_score >= 0.5:
            score = min(1.0, score + 0.05)

        proceed_t = self.thresholds.get("proceed", 0.7)
        review_t = self.thresholds.get("review", 0.4)

        # - If phase is clearly mismatched, cap score below proceed threshold to require review
        if phase_component <= 0.2:
            score = min(score, proceed_t - 0.01)

        if score >= proceed_t:
            decision: AlignmentDecision = "proceed"
        elif score >= review_t:
            decision = "review"
        else:
            decision = "block"
            if not reasons:
                reasons.append("Alignment confidence too low for autonomous execution.")

        assessment = AlignmentAssessment(
            decision=decision,
            score=round(score, 3),
            reasons=reasons,
            constraint_hits=constraint_hits,
            matches=matches,
            phase_alignment={"current": self.current_phase, "match": matched_phase},
            components=components,
        )
        return assessment

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _load_context(self) -> None:
        charter_path = self.project_root / ".ai_onboard" / "charter.json"
        plan_path = self.project_root / ".ai_onboard" / "project_plan.json"
        legacy_plan_path = self.project_root / ".ai_onboard" / "plan.json"
        state_path = self.project_root / ".ai_onboard" / "state.json"

        self.charter = utils.read_json(charter_path, default={})
        if plan_path.exists():
            self.plan = utils.read_json(plan_path, default={})
        else:
            self.plan = utils.read_json(legacy_plan_path, default={})
        self.state = utils.read_json(state_path, default={})

        self.current_phase = self._resolve_current_phase()
        self.max_complexity = str(self.charter.get("max_complexity", "")).lower()
        self.allowed_technologies = {
            str(t).lower() for t in self.charter.get("technologies", []) if isinstance(t, str)
        }
        self.non_features = [str(x).lower() for x in self.charter.get("non_features", []) if isinstance(x, str)]

        self._charter_candidates = list(self._iter_charter_candidates())
        self._wbs_candidates = list(self._iter_wbs_candidates())

    def _resolve_current_phase(self) -> Optional[str]:
        if isinstance(self.plan, dict):
            workflow = self.plan.get("workflow") or {}
            if isinstance(workflow, dict):
                phase = workflow.get("current_phase")
                if phase:
                    return str(phase).lower()
        phase = self.state.get("phase") or self.state.get("state")
        if phase:
            return str(phase).lower()
        return None

    # ---------- Candidate Construction -------------------------------- #

    def _iter_charter_candidates(self) -> Iterable[_Candidate]:
        charter = self.charter if isinstance(self.charter, dict) else {}
        description = charter.get("description")
        if isinstance(description, str) and description.strip():
            yield _Candidate(label="Charter Description", text=description)

        objectives = charter.get("objectives") or charter.get("goals") or []
        if isinstance(objectives, list):
            for idx, objective in enumerate(objectives, start=1):
                if isinstance(objective, str) and objective.strip():
                    yield _Candidate(
                        label=f"Objective {idx}",
                        text=objective,
                        metadata={"objective_index": str(idx)},
                    )

        outcomes = charter.get("top_outcomes") or []
        if isinstance(outcomes, list):
            for idx, outcome in enumerate(outcomes, start=1):
                if isinstance(outcome, str) and outcome.strip():
                    yield _Candidate(
                        label=f"Outcome {idx}",
                        text=outcome,
                        metadata={"outcome_index": str(idx)},
                    )

    def _iter_wbs_candidates(self) -> Iterable[_Candidate]:
        plan = self.plan if isinstance(self.plan, dict) else {}
        wbs = plan.get("work_breakdown_structure")
        if isinstance(wbs, dict):
            for phase_id, phase in wbs.items():
                if not isinstance(phase, dict):
                    continue
                phase_name = str(phase.get("name", phase_id))
                phase_desc = str(phase.get("description", ""))
                if phase_desc:
                    yield _Candidate(
                        label=phase_name,
                        text=phase_desc,
                        metadata={"phase": phase_name.lower()},
                    )
                subtasks = phase.get("subtasks") or {}
                if isinstance(subtasks, dict):
                    for task_id, task in subtasks.items():
                        if not isinstance(task, dict):
                            continue
                        task_name = str(task.get("name", task_id))
                        task_desc = str(task.get("description", task_name))
                        yield _Candidate(
                            label=task_name,
                            text=task_desc,
                            metadata={"phase": phase_name.lower(), "task_id": str(task_id)},
                        )
        # Legacy plan.json format may have a flat "tasks" list.
        tasks = plan.get("tasks")
        if isinstance(tasks, list):
            for task in tasks:
                if not isinstance(task, dict):
                    continue
                task_name = str(task.get("name") or task.get("title") or task.get("id") or "task")
                task_desc = str(task.get("description") or task_name)
                phase = str(task.get("phase") or task.get("category") or "").lower() or None
                yield _Candidate(
                    label=task_name,
                    text=task_desc,
                    metadata={"phase": phase} if phase else {},
                )

    # ---------- Evaluation Helpers ------------------------------------ #

    def _check_constraints(self, suggestion: str) -> List[str]:
        """Return a list of constraint hits (each hit is a reason)."""
        text = suggestion.lower()
        hits: List[str] = []
        for item in self.non_features:
            if item and item in text:
                hits.append(f"Non-feature '{item}' detected")

        scope = str(self.charter.get("scope", "")).lower()
        if scope in {"minimal", "simple"}:
            if "enterprise" in text or "multi-tenant" in text:
                hits.append("Suggestion exceeds declared scope (minimal/simple project)")

        return hits

    def _score_candidates(
        self, suggestion: str, candidates: Iterable[_Candidate], *, top_k: int = 3
    ) -> List[AlignmentMatch]:
        results: List[Tuple[float, _Candidate]] = []
        for candidate in candidates:
            similarity = self.scorer.score(suggestion, candidate.text)
            if similarity <= 0.0:
                continue
            results.append((similarity, candidate))
        results.sort(key=lambda pair: pair[0], reverse=True)
        matches = [
            AlignmentMatch(label=cand.label, similarity=round(sim, 3), metadata=cand.metadata)
            for sim, cand in results[:top_k]
        ]
        return matches

    def _phase_component(self, best_task: Optional[AlignmentMatch]) -> Tuple[float, Optional[str], Optional[str]]:
        """
        Return (component score, reason, matched_phase).

        Score ranges:
          - 1.0 : aligned with current phase
          - 0.6 : phase unknown (no info)
          - 0.2 : misaligned (future or different stream)
        """
        matched_phase = best_task.metadata.get("phase") if best_task else None
        current = self.current_phase

        if current is None:
            return 0.6, "No current phase information available.", matched_phase

        if matched_phase is None:
            return (
                0.5,
                "Suggestion does not map to any known WBS phase; manual review recommended.",
                matched_phase,
            )

        current_norm = self._normalize_phase(current)
        matched_norm = self._normalize_phase(matched_phase)

        if current_norm and matched_norm and current_norm == matched_norm:
            return 1.0, f"Phase alignment confirmed for '{matched_phase}'.", matched_phase

        return (
            0.1,
            f"Suggestion aligns with phase '{matched_phase}', but current phase is '{current}'.",
            matched_phase,
        )

    def _complexity_component(self, suggestion: str) -> Tuple[float, Optional[str]]:
        if not self.max_complexity:
            return 1.0, None

        text = suggestion.lower()
        penalty = 0.0
        reason_parts: List[str] = []

        indicators = self.COMPLEXITY_INDICATORS["advanced"]
        triggered = [indicator for indicator in indicators if indicator in text]
        if triggered and self.max_complexity in {"simple", "minimal"}:
            penalty += 0.4
            reason_parts.append(
                f"Complexity warning: terms {', '.join(triggered)} conflict with max_complexity '{self.max_complexity}'."
            )
        elif triggered and self.max_complexity in {"medium"}:
            penalty += 0.2
            reason_parts.append(
                f"Complexity caution: advanced terms {', '.join(triggered)} may exceed '{self.max_complexity}' scope."
            )

        if self.allowed_technologies:
            tokens = set(self._tokenize(suggestion))
            unknown = {token for token in tokens if token.isalpha() and token not in self.allowed_technologies}
            suspicious = unknown & {"kubernetes", "kafka", "spark", "redis", "graphql", "rust"}
            if suspicious and self.max_complexity in {"simple", "minimal"}:
                penalty += 0.2
                reason_parts.append(
                    "Technology mismatch: suggested technologies "
                    f"{', '.join(sorted(suspicious))} are not part of the approved stack."
                )

        component = max(0.0, 1.0 - min(penalty, 0.9))
        reason = " ".join(reason_parts) if reason_parts else None
        return component, reason

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [token for token in re.split(r"[^\w]+", text.lower()) if token]

    @staticmethod
    def _normalize_phase(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        normalized = value.replace("-", "_").lower()
        # Heuristic token-based normalization
        tokens = set(normalized.split())
        if "build" in tokens or "build" in normalized:
            return "build"
        if "implement" in tokens or "implementation" in normalized or "develop" in normalized:
            return "development"
        if "test" in tokens or "qa" in tokens or "testing" in normalized:
            return "testing"
        if "design" in tokens:
            return "design"
        if "plan" in tokens or "planning" in normalized or "charter" in normalized:
            return "planning"
        aliases = {
            "chartered": "planning",
            "planned": "planning",
            "executing": "development",
            "development": "development",
            "design": "design",
            "testing": "testing",
            "qa": "testing",
            "deployment": "delivery",
            "delivery": "delivery",
        }
        return aliases.get(normalized, normalized)


_DETECTOR_CACHE: Dict[Path, VisionAlignmentDetector] = {}


def get_vision_alignment_detector(project_root: Path) -> VisionAlignmentDetector:
    """Return a memoized instance of VisionAlignmentDetector for this root."""
    root = Path(project_root).resolve()
    detector = _DETECTOR_CACHE.get(root)
    if detector is None:
        detector = VisionAlignmentDetector(root)
        _DETECTOR_CACHE[root] = detector
    return detector
