from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import utils


def _should_use_codebase_analysis(root: Path) -> bool:
    """
    Determine if codebase analysis should be used based on project characteristics.

    Returns True if the project appears to be an existing codebase that would benefit
    from intelligent planning.
    """
    source_extensions = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".swift",
        ".kt",
        ".scala",
        ".clj",
    }

    source_files = 0

    # Check for source files
    for file_path in root.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in source_extensions:
            # Skip common directories
            if not any(
                skip in str(file_path)
                for skip in [
                    "__pycache__",
                    "node_modules",
                    ".git",
                    "dist",
                    "build",
                    ".vscode",
                    ".idea",
                    "target",
                    "out",
                ]
            ):
                source_files += 1

    # Use analysis if significant codebase exists
    if source_files > 10:
        return True

    # Check for package files that indicate existing project
    package_indicators = [
        "requirements.txt",
        "package.json",
        "pyproject.toml",
        "Cargo.toml",
        "composer.json",
        "Gemfile",
        "go.mod",
        "pom.xml",
        "build.gradle",
    ]

    for indicator in package_indicators:
        if (root / indicator).exists():
            return True

    # Check for common project structure patterns
    structure_indicators = [
        "src/",
        "lib/",
        "app/",
        "packages/",
        "modules/",
        "components/",
        "services/",
        "models/",
        "controllers/",
        "utils/",
        "helpers/",
    ]

    for indicator in structure_indicators:
        if (root / indicator).is_dir():
            return True

    # Default to simple planning for new/empty projects
    return False


def build(root: Path, analyze_codebase: Optional[bool] = None) -> dict:
    ch = utils.read_json(root / ".ai_onboard" / "charter.json", default=None)
    if not ch:
        raise SystemExit("Missing charter. Run: python -m ai_onboard charter")

    # Enforce methodology decision if not specified in charter
    if not ch.get("preferred_methodology"):
        from ..ai_integration.decision_enforcer import get_decision_enforcer

        enforcer = get_decision_enforcer(root)

        # Create methodology decision point
        from ..ai_integration.decision_enforcer import DecisionPoint

        methodology_decision = DecisionPoint(
            name="methodology_choice",
            question="Which project methodology should I use?",
            options={
                "agile": "Agile - Iterative development, flexible scope",
                "waterfall": "Waterfall - Sequential phases, fixed scope",
                "kanban": "Kanban - Continuous flow, visual workflow",
            },
            default="agile",  # Sensible default
        )
        enforcer.register_decision(methodology_decision)

        # Enforce the decision
        result = enforcer.enforce_decision(
            decision_name="methodology_choice",
            context={"project_name": ch.get("project_name", "Unknown")},
            agent_id="planning_system",
        )

        if result.proceed and result.response:
            # Extract user's choice
            user_responses = result.response.get("user_responses", ["agile"])
            methodology = user_responses[0] if user_responses else "agile"
            ch["preferred_methodology"] = methodology
            print(f"✅ Using {methodology} methodology (from your input)")
        else:
            # User stopped - use default
            ch["preferred_methodology"] = "agile"
            print("⚠️  Using agile methodology (default)")

    # Auto-detect if codebase analysis should be used
    if analyze_codebase is None:
        analyze_codebase = _should_use_codebase_analysis(root)
        if analyze_codebase:
            print("Existing codebase detected - using intelligent planning")
            print("   (Use --no-analyze-codebase to skip analysis)")
        else:
            print("New project detected - using charter-based planning")
            print("   (Use --analyze-codebase to force analysis)")

    # Optional codebase analysis
    codebase_data = None
    if analyze_codebase:
        try:
            from .codebase_analyzer import analyze_codebase_structure

            codebase_data = analyze_codebase_structure(root)
        except Exception as e:
            print(f"[WARNING] Codebase analysis failed: {e}")

    # Generate charter - aware work breakdown structure
    wbs = _generate_charter_aware_wbs(ch, codebase_data)

    # Generate charter - aware milestones
    milestones = _generate_charter_aware_milestones(ch, codebase_data)

    # Generate charter - aware risks
    risks = _generate_charter_aware_risks(ch, codebase_data)

    # Generate detailed project tasks
    tasks = _generate_detailed_tasks(ch, wbs, codebase_data)

    # Calculate dependencies and critical path
    dependency_analysis = _analyze_dependencies(tasks, codebase_data)

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

    # Include codebase analysis if available
    if codebase_data:
        plan["codebase_analysis"] = codebase_data
    utils.write_json(root / ".ai_onboard" / "plan.json", plan)
    return plan


def _generate_charter_aware_wbs(
    charter: dict, codebase_data: Optional[Dict[str, Any]] = None
) -> list:
    """Generate work breakdown structure based on charter content and codebase analysis."""
    wbs = []

    # Core foundation tasks
    wbs.append({"id": "C1", "name": "Core system foundation", "deps": []})

    # Adapt based on codebase analysis if available
    if codebase_data:
        languages = codebase_data.get("languages", [])
        frameworks = codebase_data.get("frameworks", [])
        modules = codebase_data.get("modules", [])
        complexity = codebase_data.get("complexity_score", 0.0)

        # Add language-specific phases
        if "python" in languages:
            wbs.append(
                {"id": "C2", "name": "Python application foundation", "deps": ["C1"]}
            )
        elif "javascript" in languages or "typescript" in languages:
            wbs.append(
                {"id": "C2", "name": "Web application foundation", "deps": ["C1"]}
            )

        # Add framework-specific phases
        if "react" in frameworks:
            wbs.append(
                {"id": "C3", "name": "React frontend setup", "deps": ["C1", "C2"]}
            )
        elif "django" in frameworks:
            wbs.append(
                {"id": "C3", "name": "Django backend setup", "deps": ["C1", "C2"]}
            )

        # Add module-specific phases based on existing modules
        if len(modules) > 5:
            wbs.append(
                {"id": "C4", "name": "Multi-module architecture", "deps": ["C1"]}
            )

        # Add testing based on test coverage
        test_coverage = codebase_data.get("test_coverage", 0.0)
        if test_coverage < 30:
            wbs.append(
                {"id": "C5", "name": "Testing infrastructure setup", "deps": ["C1"]}
            )
    else:
        # Fallback to charter-based WBS
        vision_text = str(charter.get("vision", "")).lower()
        objectives = [str(obj).lower() for obj in charter.get("objectives", [])]

        # Vision and alignment tasks
        if charter.get("vision"):
            wbs.append({"id": "C2", "name": "Vision alignment system", "deps": ["C1"]})

        # Gate system improvements
        if any("gate" in obj for obj in objectives):
            wbs.append(
                {"id": "C3", "name": "Enhanced gate system", "deps": ["C1", "C2"]}
            )

        # AI agent collaboration
        if any("agent" in obj for obj in objectives):
            wbs.append(
                {
                    "id": "C4",
                    "name": "AI agent collaboration features",
                    "deps": ["C1", "C2"],
                }
            )

        # Continuous improvement
        if any("improvement" in obj for obj in objectives):
            wbs.append(
                {
                    "id": "C5",
                    "name": "Continuous improvement system",
                    "deps": ["C1", "C2"],
                }
            )

        # Cursor AI integration
        if "cursor" in str(charter.get("constraints", {})).lower():
            wbs.append(
                {"id": "C6", "name": "Cursor AI integration", "deps": ["C1", "C4"]}
            )

        # Documentation and usability
        wbs.append(
            {
                "id": "C7",
                "name": "Documentation and user experience",
                "deps": ["C1", "C2", "C3"],
            }
        )

        # System robustness and self - improvement
        wbs.append(
            {
                "id": "C8",
                "name": "System robustness and self - improvement",
                "deps": ["C1", "C2", "C4"],
            }
        )

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

    # System robustness and self - improvement
    wbs.append(
        {
            "id": "C8",
            "name": "System robustness and self - improvement",
            "deps": ["C1", "C2", "C4"],
        }
    )

    return wbs


def _generate_charter_aware_milestones(
    charter: dict, codebase_data: Optional[Dict[str, Any]] = None
) -> list:
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
        {
            "name": "Production Ready",
            "description": "System ready for real - world use",
        },
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


def _generate_charter_aware_risks(
    charter: dict, codebase_data: Optional[Dict[str, Any]] = None
) -> list:
    """Generate risks based on charter content and constraints."""
    risks = []

    # Budget constraints
    if "low cost" in str(charter.get("constraints", {})).lower():
        risks.append(
            {
                "id": "R1",
                "desc": "Budget constraints limiting tool choices",
                "mitigation": "Focus on free / open - source solutions",
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


def _generate_detailed_tasks(
    charter: dict, wbs: list, codebase_data: Optional[Dict[str, Any]] = None
) -> list:
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
                "name": "Set up version control and CI / CD",
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


def _analyze_dependencies(
    tasks: list, codebase_data: Optional[Dict[str, Any]] = None
) -> dict:
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
    wbs_groups: Dict[str, List[Dict[str, Any]]] = {}
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
    type_groups: Dict[str, List[Dict[str, Any]]] = {}
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
