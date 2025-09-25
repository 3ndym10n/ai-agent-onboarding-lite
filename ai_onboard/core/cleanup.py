import shutil
from pathlib import Path
from typing import Any, Dict, List

from . import utils
from .dependency_checker import check_cleanup_dependencies
from .unicode_utils import print_content, print_status

# CRITICAL: Never delete these files / directories
# Based on AGENTS.md protected paths - ZERO TOLERANCE FOR DELETION
CRITICAL_PATTERNS = {
    # Core ai_onboard system (NEVER DELETE - SYSTEM BREAKS WITHOUT THESE)
    "ai_onboard/",
    ".ai_onboard/",
    "ai_onboard/__init__.py",
    "ai_onboard/__main__.py",
    "ai_onboard/VERSION",
    "ai_onboard/cli/commands.py",
    "ai_onboard/core/utils.py",
    "ai_onboard/core/state.py",
    "ai_onboard/core/telemetry.py",
    "ai_onboard/core/validation_runtime.py",
    "ai_onboard/core/policy_engine.py",
    "ai_onboard/core/registry.py",
    "ai_onboard/policies/base.json",
    # Protected directories from AGENTS.md
    ".github/",
    ".github/workflows/",
    "ai_onboard/cli/",
    "ai_onboard/core/",
    "ai_onboard/plugins/",
    "ai_onboard/plugins/conventions",
    "ai_onboard/plugins/library_module",
    "ai_onboard/plugins/ui_frontend",
    "ai_onboard/policies/",
    "ai_onboard/policies/overlays/",
    "ai_onboard/schemas/",
    # Project state files (CRITICAL - SYSTEM CANNOT FUNCTION WITHOUT THESE)
    ".ai_onboard/charter.json",
    ".ai_onboard/project_plan.json",
    ".ai_onboard/state.json",
    ".ai_onboard/analysis.json",
    ".ai_onboard/roadmap.json",
    ".ai_onboard/pattern_database.json",
    ".ai_onboard/adaptive_config.json",
    ".ai_onboard/agent_profiles.json",
    # Learning and telemetry data (CRITICAL FOR SYSTEM IMPROVEMENT)
    ".ai_onboard/learning/",
    ".ai_onboard/metrics.jsonl",
    ".ai_onboard/telemetry/",
    ".ai_onboard/debug_log.jsonl",
    ".ai_onboard/decision_log.jsonl",
    ".ai_onboard/agent_errors.jsonl",
    ".ai_onboard/task_execution_log.jsonl",
    ".ai_onboard/tool_usage.jsonl",
    # Configuration files (CRITICAL FOR SYSTEM OPERATION)
    ".ai_onboard/collaboration_config.json",
    ".ai_onboard/confidence_model.json",
    ".ai_onboard/cursor_config.json",
    # Version control (NEVER DELETE)
    ".git/",
    ".gitignore",
    # Project configuration (NEVER DELETE)
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    # Documentation (NEVER DELETE)
    "README*",
    "README.md",
    "AGENTS.md",
    "LICENSE*",
    "CHANGELOG*",
    # CI / CD (NEVER DELETE)
    ".github/",
    ".gitlab-ci.yml",
    ".travis.yml",
    "azure-pipelines.yml",
    # Environment files (NEVER DELETE)
    ".env*",
    "venv/",
    "env/",
    "ENV/",
    # IDE / Editor configs (NEVER DELETE)
    ".vscode/",
    ".idea/",
    ".editorconfig",
    # OS files (NEVER DELETE)
    ".DS_Store",
    "Thumbs.db",
}

# Common non - critical patterns that can be safely removed
NON_CRITICAL_PATTERNS = {
    # Build artifacts
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "build/",
    "dist/",
    "*.egg - info/",
    "*.egg",
    # Test artifacts
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    ".tox/",
    "coverage.xml",
    # Temporary files
    "*.tmp",
    "*.temp",
    "*.log",
    "*.bak",
    "*.swp",
    "*.swo",
    "*~",
    # Node.js artifacts
    "node_modules/",
    "npm - debug.log*",
    "yarn - debug.log*",
    "yarn - error.log*",
    # Python virtual environments (user - created)
    "venv*/",
    "env*/",
    "ENV*/",
    ".venv/",
    ".env/",
}


def is_critical(path: Path, root: Path) -> bool:
    """Check if a path is critical and should never be deleted."""
    rel_path = path.relative_to(root)
    rel_str = str(rel_path).replace("\\", "/")

    # Check exact matches first
    if rel_str in CRITICAL_PATTERNS:
        return True

    # Check pattern matches
    for pattern in CRITICAL_PATTERNS:
        if pattern.endswith("/"):
            # Directory pattern
            if rel_str.startswith(pattern) or rel_str == pattern.rstrip("/"):
                return True
        else:
            # File pattern
            if rel_str == pattern or rel_str.endswith(pattern):
                return True

    return False


def is_non_critical(path: Path, root: Path) -> bool:
    """Check if a path matches non - critical patterns that can be safely removed."""
    rel_path = path.relative_to(root)
    rel_str = str(rel_path).replace("\\", "/")

    for pattern in NON_CRITICAL_PATTERNS:
        if pattern.endswith("/"):
            # Directory pattern
            if rel_str.startswith(pattern) or rel_str == pattern.rstrip("/"):
                return True
        else:
            # File pattern
            if rel_str == pattern or rel_str.endswith(pattern):
                return True

    return False


def scan_for_cleanup(root: Path) -> Dict[str, List[Path]]:
    """Scan the project directory and categorize files for cleanup."""
    critical_files = []
    non_critical_files = []
    unknown_files = []

    for path in root.rglob("*"):
        if path.is_file():
            if is_critical(path, root):
                critical_files.append(path)
            elif is_non_critical(path, root):
                non_critical_files.append(path)
            else:
                unknown_files.append(path)
        elif path.is_dir():
            if is_critical(path, root):
                critical_files.append(path)
            elif is_non_critical(path, root):
                non_critical_files.append(path)
            else:
                # For directories, check if they're empty or only contain non-critical files
                contents = list(path.rglob("*"))
                if not contents or all(is_non_critical(p, root) for p in contents):
                    non_critical_files.append(path)
                else:
                    unknown_files.append(path)

    return {
        "critical": critical_files,
        "non_critical": non_critical_files,
        "unknown": unknown_files,
    }


def safe_cleanup(
    root: Path, dry_run: bool = True, force: bool = False
) -> Dict[str, Any]:
    """Perform safe cleanup of non - critical files with dependency checking."""
    scan_result = scan_for_cleanup(root)

    # CRITICAL: Check dependencies for all files before deletion
    if not force and scan_result["non_critical"]:
        print_content("Running dependency check on files to be deleted...", "search")

        # Check dependencies for all non - critical files
        is_safe = check_cleanup_dependencies(root, scan_result["non_critical"])

        if not is_safe:
            print_status(
                "❌ Dependency check failed - cleanup aborted for safety", "error"
            )
            return {
                "mode": "dependency_check_failed",
                "scan_result": scan_result,
                "would_delete": len(scan_result["non_critical"]),
                "protected": len(scan_result["critical"]),
                "unknown": len(scan_result["unknown"]),
                "error": "Files have dependencies - cannot safely delete",
                "recommendation": "Fix dependencies first or use --force flag (not recommended)",
            }

    if dry_run:
        print_status("✅ Dependency check passed - files are safe to delete", "success")
        return {
            "mode": "dry_run",
            "scan_result": scan_result,
            "would_delete": len(scan_result["non_critical"]),
            "protected": len(scan_result["critical"]),
            "unknown": len(scan_result["unknown"]),
        }

    # In real mode, only delete non - critical files
    deleted_count = 0
    errors = []

    for path in scan_result["non_critical"]:
        try:
            if path.is_file():
                path.unlink()
                deleted_count += 1
            elif path.is_dir():
                shutil.rmtree(path)
                deleted_count += 1
        except Exception as e:
            errors.append(f"Failed to delete {path}: {e}")

    return {
        "mode": "executed",
        "deleted_count": deleted_count,
        "errors": errors,
        "protected": len(scan_result["critical"]),
        "unknown": len(scan_result["unknown"]),
    }


def create_backup(root: Path) -> Path:
    """Create a backup of the current state before cleanup."""
    backup_dir = root / f".ai_onboard_backup_{utils.now_iso().replace(':', '-')}"
    utils.ensure_dir(backup_dir)

    # Copy all files except ai_onboard system itself
    for path in root.rglob("*"):
        if path.is_file() and not str(path).startswith(str(backup_dir)):
            rel_path = path.relative_to(root)
            backup_path = backup_dir / rel_path
            utils.ensure_dir(backup_path.parent)
            shutil.copy2(path, backup_path)

    return backup_dir
