from pathlib import Path

from . import utils


def build(root: Path) -> dict:
    ch = utils.read_json(root / ".ai_onboard" / "charter.json", default=None)
    if not ch:
        raise SystemExit("Missing charter. Run: python -m ai_onboard charter")

    # Generate charter-aware work breakdown structure
    wbs = _generate_charter_aware_wbs(ch)

    # Generate charter-aware milestones
    milestones = _generate_charter_aware_milestones(ch)

    # Generate charter-aware risks
    risks = _generate_charter_aware_risks(ch)

    # Generate detailed project tasks
    tasks = _generate_detailed_tasks(ch, wbs)

    # Calculate dependencies and critical path
    dependency_analysis = _analyze_dependencies(tasks)

    plan = {
        "methodology": ch.get("preferred_methodology", "agile"),
        "wbs": wbs,
        "tasks": tasks,
        "dependencies": dependency_analysis["dependencies"],
        "critical_path": dependency_analysis["critical_path"],
        "parallel_work": dependency_analysis["parallel_work"],
        "milestones": milestones,
        "risks": risks,
        "resources": {
            "roles": ["owner", "dev", "reviewer"],
            "limits": {"allowExec": False},
        },
        "policy_overlays": [],
        "reporting": {
            "cadence": "weekly",
            "artifacts": ["progress.md", "metrics.json"],
        },
    }
    utils.write_json(root / ".ai_onboard" / "plan.json", plan)
    return plan


def _generate_charter_aware_wbs(charter: dict) -> list:
    """Generate work breakdown structure based on charter content."""
    wbs = []

    # Core foundation tasks
    wbs.append({"id": "C1", "name": "Core system foundation", "deps": []})

    # Vision and alignment tasks
    if charter.get("vision"):
        wbs.append({"id": "C2", "name": "Vision alignment system", "deps": ["C1"]})

    # Gate system improvements
    if "gate" in str(charter.get("objectives", [])).lower():
        wbs.append({"id": "C3", "name": "Enhanced gate system", "deps": ["C1", "C2"]})

    # AI agent collaboration
    if "agent" in str(charter.get("objectives", [])).lower():
        wbs.append(
            {
                "id": "C4",
                "name": "AI agent collaboration features",
                "deps": ["C1", "C2"],
            }
        )

    # Continuous improvement
    if "improvement" in str(charter.get("objectives", [])).lower():
        wbs.append(
            {"id": "C5", "name": "Continuous improvement system", "deps": ["C1", "C2"]}
        )

    # Cursor AI integration
    if "cursor" in str(charter.get("constraints", {})).lower():
        wbs.append({"id": "C6", "name": "Cursor AI integration", "deps": ["C1", "C4"]})

    # Documentation and usability
    wbs.append(
        {
            "id": "C7",
            "name": "Documentation and user experience",
            "deps": ["C1", "C2", "C3"],
        }
    )

    # System robustness and self-improvement
    wbs.append(
        {
            "id": "C8",
            "name": "System robustness and self-improvement",
            "deps": ["C1", "C2", "C4"],
        }
    )

    return wbs


def _generate_charter_aware_milestones(charter: dict) -> list:
    """Generate milestones based on charter content."""
    milestones = [
        {
            "name": "Vision Confirmation",
            "description": "Project vision and objectives defined",
        },
        {
            "name": "Core System Ready",
            "description": "Basic system functionality implemented",
        },
        {
            "name": "AI Agent Integration",
            "description": "AI agent collaboration features working",
        },
        {"name": "Production Ready", "description": "System ready for real-world use"},
    ]

    # Add specific milestones based on top outcomes
    top_outcomes = charter.get("top_outcomes", [])
    if any("alignment" in outcome.lower() for outcome in top_outcomes):
        milestones.append(
            {
                "name": "Alignment System Complete",
                "description": "AI agent alignment features fully implemented",
            }
        )

    return milestones


def _generate_charter_aware_risks(charter: dict) -> list:
    """Generate risks based on charter content and constraints."""
    risks = []

    # Budget constraints
    if "low cost" in str(charter.get("constraints", {})).lower():
        risks.append(
            {
                "id": "R1",
                "desc": "Budget constraints limiting tool choices",
                "mitigation": "Focus on free/open-source solutions",
                "severity": "M",
            }
        )

    # Complexity risk
    if "complex" in str(charter.get("success_metrics", [])).lower():
        risks.append(
            {
                "id": "R2",
                "desc": "System becoming too complex for users",
                "mitigation": "Keep interface simple, hide complexity",
                "severity": "H",
            }
        )

    # Integration risks
    if "cursor" in str(charter.get("constraints", {})).lower():
        risks.append(
            {
                "id": "R3",
                "desc": "Cursor AI integration challenges",
                "mitigation": "Test integration early and often",
                "severity": "M",
            }
        )

    return risks


def _generate_detailed_tasks(charter: dict, wbs: list) -> list:
    """Generate detailed project tasks from WBS items."""
    tasks = []
    task_id = 1

    # Map WBS items to detailed tasks
    wbs_task_map = {
        "C1": [
            {"name": "Set up project structure", "effort_days": 2, "type": "setup"},
            {
                "name": "Configure development environment",
                "effort_days": 1,
                "type": "setup",
            },
            {
                "name": "Set up version control and CI/CD",
                "effort_days": 1,
                "type": "setup",
            },
        ],
        "C2": [
            {
                "name": "Design vision interrogation system",
                "effort_days": 3,
                "type": "design",
            },
            {
                "name": "Implement vision clarity scoring",
                "effort_days": 2,
                "type": "development",
            },
            {
                "name": "Create vision validation logic",
                "effort_days": 2,
                "type": "development",
            },
        ],
        "C3": [
            {
                "name": "Enhance gate system timeout handling",
                "effort_days": 1,
                "type": "development",
            },
            {
                "name": "Improve gate response processing",
                "effort_days": 2,
                "type": "development",
            },
            {
                "name": "Add adaptive gate triggering",
                "effort_days": 3,
                "type": "development",
            },
        ],
        "C4": [
            {
                "name": "Design AI agent collaboration protocol",
                "effort_days": 2,
                "type": "design",
            },
            {
                "name": "Implement conversation context management",
                "effort_days": 3,
                "type": "development",
            },
            {
                "name": "Create agent decision pipeline",
                "effort_days": 4,
                "type": "development",
            },
            {
                "name": "Build user preference learning system",
                "effort_days": 5,
                "type": "development",
            },
        ],
        "C5": [
            {
                "name": "Design metrics collection system",
                "effort_days": 2,
                "type": "design",
            },
            {
                "name": "Implement Kaizen cycle automation",
                "effort_days": 3,
                "type": "development",
            },
            {
                "name": "Create optimization experiment framework",
                "effort_days": 3,
                "type": "development",
            },
        ],
        "C6": [
            {
                "name": "Research Cursor AI integration points",
                "effort_days": 2,
                "type": "research",
            },
            {
                "name": "Implement Cursor AI API integration",
                "effort_days": 4,
                "type": "development",
            },
            {
                "name": "Test integration with real Cursor workflows",
                "effort_days": 3,
                "type": "testing",
            },
        ],
        "C7": [
            {
                "name": "Create user documentation",
                "effort_days": 3,
                "type": "documentation",
            },
            {
                "name": "Design user interface improvements",
                "effort_days": 2,
                "type": "design",
            },
            {
                "name": "Implement user experience enhancements",
                "effort_days": 3,
                "type": "development",
            },
        ],
        "C8": [
            {
                "name": "Implement automatic error interception",
                "effort_days": 2,
                "type": "development",
            },
            {
                "name": "Create system capability usage tracking",
                "effort_days": 2,
                "type": "development",
            },
            {
                "name": "Build learning feedback loops",
                "effort_days": 3,
                "type": "development",
            },
            {
                "name": "Design background agent integration",
                "effort_days": 4,
                "type": "development",
            },
        ],
    }

    for wbs_item in wbs:
        wbs_id = wbs_item["id"]
        if wbs_id in wbs_task_map:
            for task_detail in wbs_task_map[wbs_id]:
                task = {
                    "id": f"T{task_id}",
                    "name": task_detail["name"],
                    "wbs_id": wbs_id,
                    "effort_days": task_detail["effort_days"],
                    "type": task_detail["type"],
                    "status": "pending",
                    "dependencies": [],
                    "assigned_to": (
                        "dev"
                        if task_detail["type"] in ["development", "testing"]
                        else "owner"
                    ),
                }
                tasks.append(task)
                task_id += 1

    return tasks


def _analyze_dependencies(tasks: list) -> dict:
    """Analyze task dependencies and identify critical path and parallel work."""

    # Define logical dependencies between task types
    type_dependencies = {
        "setup": [],
        "design": ["setup"],
        "research": ["setup"],
        "development": ["design", "research"],
        "testing": ["development"],
        "documentation": ["development"],
    }

    # Build dependency graph
    dependencies = []
    for task in tasks:
        task_type = task["type"]
        if task_type in type_dependencies:
            for dep_type in type_dependencies[task_type]:
                # Find tasks of dependency type in same WBS or earlier WBS
                for other_task in tasks:
                    if (
                        other_task["type"] == dep_type
                        and other_task["id"] != task["id"]
                        and other_task["wbs_id"] <= task["wbs_id"]
                    ):
                        dependencies.append(
                            {
                                "from": other_task["id"],
                                "to": task["id"],
                                "type": "logical",
                            }
                        )
                        task["dependencies"].append(other_task["id"])

    # Calculate critical path (longest path through project)
    critical_path = _calculate_critical_path(tasks, dependencies)

    # Identify parallel work opportunities
    parallel_work = _identify_parallel_work(tasks, dependencies)

    return {
        "dependencies": dependencies,
        "critical_path": critical_path,
        "parallel_work": parallel_work,
    }


def _calculate_critical_path(tasks: list, dependencies: list) -> list:
    """Calculate the critical path through the project."""
    # Simple critical path calculation based on effort and dependencies
    # Find longest path (simplified approach)
    critical_tasks = []

    # Group by WBS to find critical path
    wbs_groups = {}
    for task in tasks:
        wbs_id = task["wbs_id"]
        if wbs_id not in wbs_groups:
            wbs_groups[wbs_id] = []
        wbs_groups[wbs_id].append(task)

    # Critical path includes highest effort tasks in each WBS
    for wbs_id in sorted(wbs_groups.keys()):
        wbs_tasks = wbs_groups[wbs_id]
        max_task = max(wbs_tasks, key=lambda t: t["effort_days"])
        critical_tasks.append(max_task["id"])

    return critical_tasks


def _identify_parallel_work(tasks: list, dependencies: list) -> list:
    """Identify tasks that can be worked on in parallel."""
    parallel_groups = []

    # Group tasks by type that can be done in parallel
    type_groups = {}
    for task in tasks:
        task_type = task["type"]
        if task_type not in type_groups:
            type_groups[task_type] = []
        type_groups[task_type].append(task)

    # Identify parallel opportunities
    for task_type, type_tasks in type_groups.items():
        if len(type_tasks) > 1 and task_type in ["design", "research", "documentation"]:
            parallel_groups.append(
                {
                    "group_name": f"{task_type.title()} tasks",
                    "tasks": [t["id"] for t in type_tasks],
                    "can_parallel": True,
                    "reason": f"Multiple {task_type} tasks can be done simultaneously",
                }
            )

    return parallel_groups
