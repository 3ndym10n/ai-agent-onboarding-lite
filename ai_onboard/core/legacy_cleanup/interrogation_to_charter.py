"""
Interrogation to Charter Sync - Automatically syncs vision interrogation data to charter.json.

This ensures that the comprehensive interrogation data becomes the authoritative
vision source for the entire system.
"""

from pathlib import Path

from ..base import utils


def sync_interrogation_to_charter(root: Path) -> bool:
    """
    Sync vision interrogation data to charter.json.

    Returns:
        True if sync was successful, False otherwise
    """
    try:
        # Read interrogation data
        interrogation_file = root / ".ai_onboard" / "vision_interrogation.json"
        interrogation_data = utils.read_json(interrogation_file, default={})

        if interrogation_data.get("status") != "completed":
            return False

        # Extract data from interrogation responses
        vision_core = interrogation_data.get("responses", {}).get("vision_core", {})
        stakeholders = interrogation_data.get("responses", {}).get("stakeholders", {})
        scope = interrogation_data.get("responses", {}).get("scope", {})
        success = interrogation_data.get("responses", {}).get("success", {})

        # Create charter from interrogation data
        charter = {
            "version": 1,
            "project_name": root.name,
            "vision": vision_core.get("vc_02", {})
            .get("response", {})
            .get("answer", ""),
            "objectives": [
                stakeholders.get("sg_02", {}).get("response", {}).get("answer", ""),
                success.get("sc_02", {}).get("response", {}).get("answer", ""),
                "Complete AI agent orchestration system with safety and \
                    collaboration features",
            ],
            "non_goals": [
                scope.get("sb_02", {}).get("response", {}).get("answer", ""),
                "Not a replacement for human oversight",
                "Not language specific",
                "Not a plugin",
            ],
            "stakeholders": [
                {
                    "name": "Project Owner",
                    "role": "Decision Maker",
                    "decider": True,
                    "goals": stakeholders.get("sg_02", {})
                    .get("response", {})
                    .get("answer", ""),
                }
            ],
            "constraints": {
                "time": "Limited but can give time as needed",
                "budget": "Very low cost or free solutions only",
                "compliance": [
                    "Must work within cursor - ai",
                    "Python 3.8+ compatibility",
                ],
            },
            "assumptions": [
                "Users have limited programming background",
                "Users are tech - savvy but lack technical implementation knowledge",
                "AI agents need structured collaboration mechanisms",
            ],
            "success_metrics": [
                {
                    "name": "AI Drift Reduction",
                    "target": "Minimize times AI needs to be reeled back in",
                    "description": success.get("sc_01", {})
                    .get("response", {})
                    .get("answer", ""),
                },
                {
                    "name": "Feature Utilization",
                    "target": "All designed features used at least once",
                    "description": success.get("sc_02", {})
                    .get("response", {})
                    .get("answer", ""),
                },
                {
                    "name": "System Compliance",
                    "target": "System utilizes all functions in projects",
                    "description": success.get("sc_03", {})
                    .get("response", {})
                    .get("answer", ""),
                },
            ],
            "risk_appetite": "low",
            "delivery_horizon_days": 90,
            "team_size": 1,
            "preferred_methodology": "agile",
            "created_from": "vision_interrogation",
            "created_at": utils.now_iso(),
            "interrogation_insights": interrogation_data.get("insights", []),
        }

        # Write charter file
        charter_file = root / ".ai_onboard" / "charter.json"
        utils.write_json(charter_file, charter)

        return True

    except Exception as e:
        print(f"Error syncing interrogation to charter: {e}")
        return False


def auto_sync_on_completion(root: Path) -> bool:
    """
    Automatically sync when interrogation is completed.
    This should be called whenever interrogation status changes to 'completed'.
    """
    return sync_interrogation_to_charter(root)
