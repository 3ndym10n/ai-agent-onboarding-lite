import logging
from pathlib import Path
from typing import Any, Dict

from . import utils

# Set up logging for policy loading issues
logger = logging.getLogger(__name__)


def _read_policy_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "rules": [],
            "scoring": {
                "pass_threshold": 0.7,
                "weights": {"error": 1.0, "warn": 0.4, "info": 0.1},
            },
        }

    suffix = path.suffix.lower()
    try:
        if suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore
            except ImportError:
                # YAML not available - log warning and fall back to JSON if available
                logger.warning(
                    f"PyYAML not available, cannot load {path}. Consider installing PyYAML for YAML policy support."
                )

                # Try to find a JSON equivalent
                json_path = path.with_suffix(".json")
                if json_path.exists():
                    logger.info(f"Falling back to JSON equivalent: {json_path}")
                    return utils.read_json(json_path, default={}) or {}

                # Return empty policy but log the issue
                logger.error(
                    f"YAML policy {path} cannot be loaded and no JSON fallback found. Policy enforcement may be weakened."
                )
                return {}

            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}

        # Default JSON handling
        return utils.read_json(path, default={}) or {}
    except Exception as e:
        logger.error(f"Error loading policy file {path}: {e}")
        return {}


def load(root: Path) -> dict:
    manifest = utils.read_json(root / "ai_onboard.json", default={"policies": {}}) or {
        "policies": {}
    }
    base_default = "./ai_onboard/policies/base.yaml"
    base_path = Path(manifest.get("policies", {}).get("base", base_default))
    base_full = root / base_path
    # If configured base points to json but yaml exists, prefer configured; otherwise if default and json missing, try yaml
    policy = _read_policy_file(base_full)

    # Load self-preservation policies
    self_preservation_path = root / "ai_onboard" / "policies" / "self_preservation.yaml"
    if self_preservation_path.exists():
        self_preservation_policy = _read_policy_file(self_preservation_path)
        _merge(policy, self_preservation_policy)

    # Load agent prompt rules
    agent_rules_path = root / "ai_onboard" / "policies" / "agent_prompt_rules.yaml"
    if agent_rules_path.exists():
        agent_rules_policy = _read_policy_file(agent_rules_path)
        _merge(policy, agent_rules_policy)

    # Load vision interrogation rules
    vision_interrogation_path = (
        root / "ai_onboard" / "policies" / "vision_interrogation_rules.yaml"
    )
    if vision_interrogation_path.exists():
        vision_interrogation_policy = _read_policy_file(vision_interrogation_path)
        _merge(policy, vision_interrogation_policy)

    for overlay in manifest.get("policies", {}).get("overlays", []):
        o = _read_policy_file(root / Path(overlay))
        _merge(policy, o)
    # Ensure scoring defaults present
    policy.setdefault(
        "scoring",
        {"pass_threshold": 0.7, "weights": {"error": 1.0, "warn": 0.4, "info": 0.1}},
    )
    policy.setdefault("rules", [])
    return policy


def _merge(dst: dict, src: dict) -> None:
    for k, v in src.items():
        if isinstance(v, list):
            dst.setdefault(k, []).extend(v)
        elif isinstance(v, dict):
            dst.setdefault(k, {})
            _merge(dst[k], v)
        else:
            dst[k] = v
