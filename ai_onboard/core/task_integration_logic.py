"""
Task Integration Logic - Automatically maps identified tasks to appropriate project phases.

This module provides the logic for determining where new tasks should be placed
in the project Work Breakdown Structure (WBS) based on task characteristics,
dependencies, and project context.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import utils


class TaskIntegrationLogic:
    """Logic for automatically integrating identified tasks into the project WBS."""

    def __init__(self, root: Path):
        self.root = root
        self.project_plan_path = root / ".ai_onboard" / "project_plan.json"

    def integrate_task(
        self, task_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Integrate a newly identified task into the project WBS.

        Args:
            task_data: Task information including name, description, priority, etc.
            context: Additional context about how/why the task was identified

        Returns:
            Integration result with placement recommendations
        """
        from .tool_usage_tracker import track_tool_usage

        track_tool_usage(
            "task_integration_logic",
            "ai_system",
            {"action": "integrate_task", "task_name": task_data.get("name")},
            "success",
        )

        # Analyze task characteristics
        task_analysis = self._analyze_task_characteristics(task_data)

        # Determine appropriate placement
        placement_recommendation = self._determine_placement(task_analysis, context)

        # Generate integration plan
        integration_plan = self._generate_integration_plan(
            task_data, task_analysis, placement_recommendation
        )

        return {
            "task_analysis": task_analysis,
            "placement_recommendation": placement_recommendation,
            "integration_plan": integration_plan,
            "confidence_score": self._calculate_confidence(
                task_analysis, placement_recommendation
            ),
        }

    def _analyze_task_characteristics(
        self, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze task characteristics to determine its nature and requirements."""
        analysis = {
            "task_type": self._classify_task_type(task_data),
            "priority_level": self._assess_priority(task_data),
            "dependencies": self._identify_dependencies(task_data),
            "estimated_effort": self._estimate_effort(task_data),
            "critical_path_impact": self._assess_critical_path_impact(task_data),
            "phase_alignment": self._determine_phase_alignment(task_data),
            "skill_requirements": self._identify_skill_requirements(task_data),
        }
        return analysis

    def _classify_task_type(self, task_data: Dict[str, Any]) -> str:
        """Classify the task type based on its characteristics."""
        name = task_data.get("name", "").lower()
        description = task_data.get("description", "").lower()

        # Pattern-based classification
        patterns = {
            "architecture": [
                r"design",
                r"architecture",
                r"structure",
                r"framework",
                r"system.*design",
                r"component.*design",
            ],
            "implementation": [
                r"implement",
                r"build",
                r"create",
                r"develop",
                r"code",
                r"programming",
                r"development",
            ],
            "testing": [
                r"test",
                r"validation",
                r"verify",
                r"check",
                r"quality",
                r"coverage",
                r"integration.*test",
            ],
            "documentation": [
                r"doc",
                r"document",
                r"readme",
                r"guide",
                r"tutorial",
                r"example",
                r"api.*doc",
            ],
            "infrastructure": [
                r"ci",
                r"cd",
                r"pipeline",
                r"deployment",
                r"build",
                r"release",
                r"packaging",
            ],
            "security": [
                r"security",
                r"safety",
                r"protection",
                r"vulnerability",
                r"auth",
                r"permission",
                r"access",
            ],
            "performance": [
                r"performance",
                r"optimization",
                r"speed",
                r"efficiency",
                r"memory",
                r"cpu",
                r"scalability",
            ],
            "maintenance": [
                r"fix",
                r"bug",
                r"issue",
                r"repair",
                r"maintenance",
                r"refactor",
                r"cleanup",
                r"update",
            ],
        }

        combined_text = f"{name} {description}"

        for task_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, combined_text):
                    return task_type

        # Default classification
        return "general"

    def _assess_priority(self, task_data: Dict[str, Any]) -> str:
        """Assess the priority level of the task."""
        priority_indicators = {
            "critical": [
                r"critical",
                r"blocker",
                r"blocking",
                r"must.*have",
                r"essential",
                r"required",
                r"mandatory",
            ],
            "high": [
                r"high.*priority",
                r"important",
                r"urgent",
                r"should.*have",
                r"recommended",
                r"valuable",
            ],
            "medium": [r"medium", r"nice.*to.*have", r"enhancement", r"improvement"],
            "low": [r"low.*priority", r"optional", r"future", r"eventually"],
        }

        text_to_check = (
            f"{task_data.get('name', '')} {task_data.get('description', '')}".lower()
        )

        for priority, patterns in priority_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text_to_check):
                    return priority

        # Default to medium if no clear indicators
        return "medium"

    def _identify_dependencies(self, task_data: Dict[str, Any]) -> List[str]:
        """Identify potential dependencies for the task."""
        dependencies = []

        text = f"{task_data.get('name', '')} {task_data.get('description', '')}".lower()

        # Look for explicit dependency mentions
        dep_patterns = [
            r"depends.*on",
            r"requires",
            r"needs",
            r"after",
            r"following",
            r"prerequisite",
            r"before.*can",
        ]

        for pattern in dep_patterns:
            if re.search(pattern, text):
                dependencies.append("explicit_dependency_found")

        # Look for phase-specific dependencies
        if re.search(r"test|validation|verify", text):
            dependencies.append("implementation_complete")

        if re.search(r"deploy|release|production", text):
            dependencies.append("testing_complete")

        if re.search(r"document|readme|guide", text):
            dependencies.append("feature_complete")

        return dependencies

    def _estimate_effort(self, task_data: Dict[str, Any]) -> str:
        """Estimate the effort level required for the task."""
        text = f"{task_data.get('name', '')} {task_data.get('description', '')}".lower()

        # Size indicators
        if re.search(r"(major|large|complex|extensive|comprehensive)", text):
            return "large"
        elif re.search(r"(medium|moderate|significant)", text):
            return "medium"
        elif re.search(r"(small|simple|minor|quick|trivial)", text):
            return "small"

        # Type-based estimation
        task_type = self._classify_task_type(task_data)
        type_effort_map = {
            "architecture": "large",
            "implementation": "large",
            "testing": "medium",
            "documentation": "small",
            "infrastructure": "medium",
            "security": "large",
            "performance": "large",
            "maintenance": "medium",
        }

        return type_effort_map.get(task_type, "medium")

    def _assess_critical_path_impact(self, task_data: Dict[str, Any]) -> str:
        """Assess if this task impacts the critical path."""
        priority = task_data.get("priority", "medium")
        if priority == "critical":
            return "critical_path"

        text = f"{task_data.get('name', '')} {task_data.get('description', '')}".lower()

        # Critical path indicators
        critical_indicators = [
            r"blocker",
            r"blocking",
            r"gates",
            r"prevents",
            r"critical.*path",
            r"must.*complete",
            r"dependency.*chain",
        ]

        for indicator in critical_indicators:
            if re.search(indicator, text):
                return "critical_path"

        return "non_critical"

    def _determine_phase_alignment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine which project phase this task aligns with."""
        task_type = self._classify_task_type(task_data)

        # Phase mapping based on task type
        phase_mapping = {
            "architecture": {"phase": "1.0", "confidence": 0.9},
            "implementation": {"phase": "2.0", "confidence": 0.8},
            "testing": {"phase": "4.0", "confidence": 0.9},
            "documentation": {"phase": "6.0", "confidence": 0.8},
            "infrastructure": {"phase": "4.0", "confidence": 0.7},
            "security": {"phase": "2.0", "confidence": 0.8},
            "performance": {"phase": "5.0", "confidence": 0.7},
            "maintenance": {"phase": "4.0", "confidence": 0.6},
        }

        # Check for specific keywords that might override type-based mapping
        text = f"{task_data.get('name', '')} {task_data.get('description', '')}".lower()

        keyword_phase_mapping = {
            "vision|charter|planning": "3.0",
            "validation|quality|testing": "4.0",
            "optimization|performance|tuning": "5.0",
            "documentation|user.*experience|ui|ux": "6.0",
        }

        for keywords, phase in keyword_phase_mapping.items():
            if re.search(keywords, text):
                return {"phase": phase, "confidence": 0.8, "reason": "keyword_match"}

        # Return type-based mapping
        if task_type in phase_mapping:
            mapping = phase_mapping[task_type].copy()
            mapping["reason"] = "task_type_mapping"
            return mapping

        # Default to current active phase
        return {"phase": "4.0", "confidence": 0.5, "reason": "default_current_phase"}

    def _identify_skill_requirements(self, task_data: Dict[str, Any]) -> List[str]:
        """Identify the skills required for this task."""
        skills = []
        text = f"{task_data.get('name', '')} {task_data.get('description', '')}".lower()

        skill_patterns = {
            "python_development": [r"python", r"django", r"flask", r"fastapi"],
            "web_development": [r"javascript", r"react", r"vue", r"html", r"css"],
            "devops": [
                r"docker",
                r"kubernetes",
                r"ci.?cd",
                r"jenkins",
                r"github.*actions",
            ],
            "database": [r"sql", r"mongodb", r"postgresql", r"redis", r"database"],
            "ai_ml": [r"machine.*learning", r"ai", r"neural", r"model", r"training"],
            "security": [
                r"security",
                r"authentication",
                r"authorization",
                r"encryption",
            ],
            "testing": [r"unit.*test", r"integration.*test", r"test.*automation"],
            "documentation": [r"technical.*writing", r"documentation", r"api.*doc"],
        }

        for skill, patterns in skill_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    if skill not in skills:
                        skills.append(skill)

        return skills if skills else ["general_development"]

    def _determine_placement(
        self, task_analysis: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Determine the best placement for the task in the WBS."""
        phase_alignment = task_analysis["phase_alignment"]

        # Get current project structure
        project_plan = utils.read_json(self.project_plan_path, default={})
        wbs = project_plan.get("work_breakdown_structure", {})

        recommended_phase = phase_alignment["phase"]

        # Check if the recommended phase exists and is active
        if recommended_phase not in wbs:
            # Find the most appropriate existing phase
            recommended_phase = self._find_best_existing_phase(task_analysis, wbs)

        # Determine if this should be a new subtask or modify existing structure
        placement_type, placement_details = self._determine_placement_type(
            task_analysis, recommended_phase, wbs
        )

        return {
            "recommended_phase": recommended_phase,
            "placement_type": placement_type,  # "new_subtask", "new_phase", "modify_existing"
            "placement_details": placement_details,
            "confidence": phase_alignment["confidence"],
            "reasoning": phase_alignment["reason"],
        }

    def _find_best_existing_phase(
        self, task_analysis: Dict[str, Any], wbs: Dict[str, Any]
    ) -> str:
        """Find the best existing phase for a task when the recommended phase doesn't exist."""
        task_type = task_analysis["task_type"]

        # Phase preference based on task type
        type_preferences = {
            "architecture": ["1.0", "2.0", "3.0"],
            "implementation": ["2.0", "4.0", "1.0"],
            "testing": ["4.0", "2.0", "5.0"],
            "documentation": ["6.0", "3.0", "5.0"],
            "infrastructure": ["4.0", "1.0", "5.0"],
            "security": ["2.0", "4.0", "1.0"],
            "performance": ["5.0", "4.0", "2.0"],
            "maintenance": ["4.0", "5.0", "2.0"],
        }

        preferences = type_preferences.get(task_type, ["4.0", "5.0", "6.0"])

        # Return first existing preference
        for phase in preferences:
            if phase in wbs:
                return phase

        # Fallback to the last phase number
        phase_numbers = sorted(
            [float(k) for k in wbs.keys() if k.replace(".", "").isdigit()]
        )
        return f"{int(phase_numbers[-1]) + 1}.0" if phase_numbers else "4.0"

    def _determine_placement_type(
        self, task_analysis: Dict[str, Any], phase: str, wbs: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Determine how the task should be placed within the phase."""
        phase_data = wbs.get(phase, {})
        existing_subtasks = phase_data.get("subtasks", {})

        task_type = task_analysis["task_type"]
        priority = task_analysis["priority_level"]

        # For critical tasks, create new subtasks
        if (
            priority == "critical"
            or task_analysis["critical_path_impact"] == "critical_path"
        ):
            new_subtask_id = self._generate_next_subtask_id(phase, existing_subtasks)
            return "new_subtask", {
                "subtask_id": new_subtask_id,
                "parent_phase": phase,
                "reason": "critical_task_requires_dedicated_subtask",
            }

        # Check if there's an existing subtask that matches well
        best_match = self._find_best_subtask_match(task_analysis, existing_subtasks)
        if best_match:
            return "modify_existing", {
                "existing_subtask": best_match,
                "modification_type": "add_task",
                "reason": "matches_existing_subtask_scope",
            }

        # Create new subtask for medium/high priority tasks
        if priority in ["high", "medium"]:
            new_subtask_id = self._generate_next_subtask_id(phase, existing_subtasks)
            return "new_subtask", {
                "subtask_id": new_subtask_id,
                "parent_phase": phase,
                "reason": "significant_task_requires_own_subtask",
            }

        # For low priority tasks, add to existing subtask or create general one
        general_subtask = self._find_or_create_general_subtask(phase, existing_subtasks)
        if general_subtask:
            return "modify_existing", {
                "existing_subtask": general_subtask,
                "modification_type": "add_task",
                "reason": "low_priority_task_added_to_general_subtask",
            }

        # Fallback: create new subtask
        new_subtask_id = self._generate_next_subtask_id(phase, existing_subtasks)
        return "new_subtask", {
            "subtask_id": new_subtask_id,
            "parent_phase": phase,
            "reason": "fallback_new_subtask",
        }

    def _generate_next_subtask_id(
        self, phase: str, existing_subtasks: Dict[str, Any]
    ) -> str:
        """Generate the next available subtask ID for a phase."""
        if not existing_subtasks:
            return f"{phase}.1"

        # Find the highest subtask number
        existing_ids = []
        for subtask_id in existing_subtasks.keys():
            if subtask_id.startswith(f"{phase}."):
                try:
                    num = int(subtask_id.split(".")[-1])
                    existing_ids.append(num)
                except (ValueError, IndexError):
                    continue

        next_num = max(existing_ids) + 1 if existing_ids else 1
        return f"{phase}.{next_num}"

    def _find_best_subtask_match(
        self, task_analysis: Dict[str, Any], existing_subtasks: Dict[str, Any]
    ) -> Optional[str]:
        """Find the best existing subtask match for the task."""
        task_type = task_analysis["task_type"]
        task_name_lower = task_analysis.get("task_name", "").lower()

        # Look for subtasks with similar names or purposes
        for subtask_id, subtask_data in existing_subtasks.items():
            subtask_name = subtask_data.get("name", "").lower()

            # Direct name matching
            if task_type in subtask_name or any(
                word in subtask_name for word in task_name_lower.split()
            ):
                return subtask_id

            # Type-based matching
            type_keywords = {
                "testing": ["test", "validation", "quality", "verify"],
                "documentation": ["doc", "guide", "readme", "tutorial"],
                "infrastructure": ["ci", "cd", "build", "deploy"],
                "security": ["security", "auth", "safety", "protection"],
            }

            if task_type in type_keywords:
                keywords = type_keywords[task_type]
                if any(keyword in subtask_name for keyword in keywords):
                    return subtask_id

        return None

    def _find_or_create_general_subtask(
        self, phase: str, existing_subtasks: Dict[str, Any]
    ) -> Optional[str]:
        """Find or suggest creation of a general-purpose subtask."""
        # Look for existing general subtasks
        general_names = ["general", "miscellaneous", "other", "various", "additional"]

        for subtask_id, subtask_data in existing_subtasks.items():
            subtask_name = subtask_data.get("name", "").lower()
            if any(general in subtask_name for general in general_names):
                return subtask_id

        # Suggest creating a general subtask
        return None  # Caller will handle creating new subtask

    def _generate_integration_plan(
        self,
        task_data: Dict[str, Any],
        task_analysis: Dict[str, Any],
        placement: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a detailed integration plan for the task."""
        plan = {
            "task_id": self._generate_task_id(task_data, placement),
            "task_name": task_data.get("name", "Unnamed Task"),
            "task_description": task_data.get("description", ""),
            "placement": placement,
            "estimated_effort": task_analysis["estimated_effort"],
            "priority": task_analysis["priority_level"],
            "required_skills": task_analysis["skill_requirements"],
            "dependencies": task_analysis["dependencies"],
            "integration_steps": self._generate_integration_steps(placement),
            "risk_assessment": self._assess_integration_risks(task_analysis, placement),
        }

        return plan

    def _generate_task_id(
        self, task_data: Dict[str, Any], placement: Dict[str, Any]
    ) -> str:
        """Generate a unique task ID."""
        placement_type = placement["placement_type"]

        if placement_type == "new_subtask":
            # Use the subtask ID as the task ID
            return placement["placement_details"]["subtask_id"]
        elif placement_type == "modify_existing":
            # Generate a task ID within the existing subtask
            existing_subtask = placement["placement_details"]["existing_subtask"]
            return f"{existing_subtask}.1"  # Simplified - in practice would check existing tasks
        else:
            # Generate a standalone task ID
            base_id = placement["recommended_phase"]
            return f"{base_id}.task_{hash(task_data.get('name', 'unknown')) % 1000}"

    def _generate_integration_steps(self, placement: Dict[str, Any]) -> List[str]:
        """Generate the steps needed to integrate the task."""
        steps = []

        if placement["placement_type"] == "new_subtask":
            steps.extend(
                [
                    f"Create new subtask {placement['placement_details']['subtask_id']} in phase {placement['recommended_phase']}",
                    "Add task details to the subtask",
                    "Update phase completion percentage if needed",
                    "Add to critical path if high priority",
                ]
            )
        elif placement["placement_type"] == "modify_existing":
            steps.extend(
                [
                    f"Add task to existing subtask {placement['placement_details']['existing_subtask']}",
                    "Update subtask description to include new task scope",
                    "Adjust subtask completion tracking if needed",
                ]
            )
        elif placement["placement_type"] == "new_phase":
            steps.extend(
                [
                    f"Create new phase {placement['recommended_phase']}",
                    "Define phase objectives and deliverables",
                    "Add task as first subtask in new phase",
                ]
            )

        steps.extend(
            [
                "Update project dependencies and critical path",
                "Assign appropriate team member based on skills",
                "Set realistic due date based on effort estimation",
                "Update project timeline and milestones",
            ]
        )

        return steps

    def _assess_integration_risks(
        self, task_analysis: Dict[str, Any], placement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risks associated with integrating this task."""
        risks = []

        # Phase fit risk
        if placement["confidence"] < 0.7:
            risks.append(
                {
                    "type": "phase_misalignment",
                    "severity": "medium",
                    "description": f"Task may not fit well in phase {placement['recommended_phase']}",
                }
            )

        # Dependency risk
        if task_analysis["dependencies"]:
            risks.append(
                {
                    "type": "dependency_complexity",
                    "severity": (
                        "low" if len(task_analysis["dependencies"]) < 3 else "medium"
                    ),
                    "description": f"Task has {len(task_analysis['dependencies'])} dependencies to manage",
                }
            )

        # Effort estimation risk
        if (
            task_analysis["estimated_effort"] == "large"
            and task_analysis["priority_level"] == "high"
        ):
            risks.append(
                {
                    "type": "effort_priority_mismatch",
                    "severity": "medium",
                    "description": "High priority task with large effort may cause scheduling conflicts",
                }
            )

        return {
            "overall_risk_level": (
                "high"
                if any(r["severity"] == "high" for r in risks)
                else (
                    "medium" if any(r["severity"] == "medium" for r in risks) else "low"
                )
            ),
            "identified_risks": risks,
            "mitigation_suggestions": self._generate_risk_mitigations(risks),
        }

    def _generate_risk_mitigations(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Generate mitigation strategies for identified risks."""
        mitigations = []

        for risk in risks:
            if risk["type"] == "phase_misalignment":
                mitigations.append(
                    "Consider manual review of phase placement before integration"
                )
            elif risk["type"] == "dependency_complexity":
                mitigations.append(
                    "Map out dependency chain and consider breaking into smaller tasks"
                )
            elif risk["type"] == "effort_priority_mismatch":
                mitigations.append(
                    "Consider adjusting priority or breaking into smaller deliverables"
                )

        if not mitigations:
            mitigations.append(
                "No specific mitigations required - standard integration process"
            )

        return mitigations

    def _calculate_confidence(
        self, task_analysis: Dict[str, Any], placement: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score for the integration recommendation."""
        base_confidence = placement["confidence"]

        # Boost confidence for well-matched tasks
        if placement["placement_type"] == "modify_existing":
            base_confidence += 0.1

        # Boost for critical tasks in appropriate phases
        if (
            task_analysis["priority_level"] == "critical"
            and placement["placement_type"] == "new_subtask"
        ):
            base_confidence += 0.1

        # Penalize for low confidence placements
        if base_confidence < 0.6:
            base_confidence -= 0.1

        return max(0.0, min(1.0, base_confidence))


def integrate_task(
    task_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Convenience function to integrate a task using the TaskIntegrationLogic."""
    if root is None:
        root = Path.cwd()

    integrator = TaskIntegrationLogic(root)
    return integrator.integrate_task(task_data, context)
