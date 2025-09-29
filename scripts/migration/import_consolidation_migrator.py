#!/usr/bin/env python3
"""
Import Consolidation Migrator - Safe migration tool for import consolidation.

This tool provides safe migration of imports to consolidated modules, integrating
with the existing CleanupSafetyGateFramework and ContinuousImprovementValidator.

Features:
- Safe import migration with backup/rollback
- Import equivalence validation
- Gradual migration support
- Integration with existing safety gates
- Comprehensive logging and monitoring
"""
import ast
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.base.utils import ensure_dir, read_json, write_json
from ai_onboard.core.continuous_improvement.continuous_improvement_validator import (
    ContinuousImprovementValidator,
)
from ai_onboard.core.quality_safety.cleanup_safety_gates import (
    CleanupOperation,
    CleanupSafetyGateFramework,
)


class MigrationStatus(Enum):
    """Migration status tracking."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ImportType(Enum):
    """Types of imports to consolidate."""

    STDLIB = "stdlib"
    TYPING = "typing"
    DATACLASSES = "dataclasses"
    PATHLIB = "pathlib"
    THIRD_PARTY = "third_party"
    LOCAL = "local"
    OTHER = "other"


@dataclass
class ImportStatement:
    """Represents an import statement."""

    module: str
    names: List[str]
    alias: Optional[str] = None
    line_number: int = 0
    file_path: Path = None
    import_type: ImportType = ImportType.LOCAL


@dataclass
class ConsolidationTarget:
    """Target module for consolidation."""

    name: str
    imports: List[ImportStatement]
    target_file: Path
    priority: int = 1
    risk_level: str = "low"


@dataclass
class MigrationPlan:
    """Migration plan for import consolidation."""

    targets: List[ConsolidationTarget]
    backup_id: str
    validation_checks: List[str]
    rollback_plan: Dict[str, Any]
    estimated_duration: int = 0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)


class ImportConsolidationMigrator:
    """Safe import consolidation migrator with full safety integration."""

    def __init__(self, root: Path):
        self.root = root
        self.migration_log = root / ".ai_onboard" / "migration_log.jsonl"
        self.consolidation_config = root / ".ai_onboard" / "consolidation_config.json"
        self.backup_dir = root / ".ai_onboard" / "import_migration_backups"

        # Initialize safety framework
        self.safety_framework = CleanupSafetyGateFramework(root)
        self.validator = ContinuousImprovementValidator(root)

        # Ensure directories exist
        ensure_dir(self.migration_log.parent)
        ensure_dir(self.backup_dir)

        # Load configuration
        self.config = self._load_config()

        # Track migration state
        self.current_migration: Optional[MigrationPlan] = None
        self.migration_history: List[Dict[str, Any]] = []

    def _load_config(self) -> Dict[str, Any]:
        """Load consolidation configuration."""
        default_config = {
            "consolidation_targets": {
                "common_imports": {
                    "target_file": "ai_onboard/core/common_imports.py",
                    "priority": 1,
                    "risk_level": "low",
                    "imports": [
                        "pathlib.Path",
                        "typing.Dict",
                        "typing.List",
                        "typing.Optional",
                        "typing.Any",
                        "typing.Union",
                        "typing.Callable",
                        "dataclasses.dataclass",
                        "dataclasses.field",
                        "collections.deque",
                        "contextlib.contextmanager",
                    ],
                },
                "types": {
                    "target_file": "ai_onboard/core/types.py",
                    "priority": 2,
                    "risk_level": "low",
                    "imports": [
                        "typing.Dict",
                        "typing.List",
                        "typing.Optional",
                        "typing.Any",
                        "typing.Union",
                        "typing.Callable",
                        "typing.Set",
                        "typing.Iterable",
                        "typing.Tuple",
                    ],
                },
                "paths": {
                    "target_file": "ai_onboard/core/paths.py",
                    "priority": 3,
                    "risk_level": "low",
                    "imports": [
                        "pathlib.Path",
                        "pathlib.PurePath",
                        "os.path.join",
                        "os.path.exists",
                        "os.path.isdir",
                        "os.path.isfile",
                    ],
                },
            },
            "migration_settings": {
                "batch_size": 5,
                "validation_interval": 3,
                "rollback_threshold": 0.8,
                "dry_run_first": True,
            },
            "safety_checks": [
                "import_resolution",
                "syntax_validation",
                "circular_dependency",
                "functionality_test",
            ],
        }

        return read_json(self.consolidation_config, default_config)

    def analyze_consolidation_opportunities(self) -> Dict[str, Any]:
        """Analyze current codebase for consolidation opportunities."""
        print("🔍 Analyzing consolidation opportunities...")

        # Get all Python files
        python_files = list(self.root.rglob("*.py"))
        python_files = [
            f
            for f in python_files
            if not f.name.startswith("__")
            and "test" not in str(f)
            and "__pycache__" not in str(f)
            and ".git" not in str(f)
            and "build" not in str(f)
            and "dist" not in str(f)
            and ".egg-info" not in str(f)
            and "node_modules" not in str(f)
            and "venv" not in str(f)
            and ".ai_onboard" not in str(f)  # Exclude generated artifacts
            and f.is_file()  # Only actual files, not directories
        ]

        # Analyze imports in each file
        import_analysis = {}
        total_imports = 0
        consolidation_candidates = {}

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                file_imports = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_stmt = ImportStatement(
                                module=alias.name,
                                names=[alias.name],
                                alias=alias.asname,
                                line_number=node.lineno,
                                file_path=file_path,
                                import_type=self._classify_import(alias.name),
                            )
                            file_imports.append(import_stmt)
                            total_imports += 1

                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            import_stmt = ImportStatement(
                                module=module,
                                names=[alias.name],
                                alias=alias.asname,
                                line_number=node.lineno,
                                file_path=file_path,
                                import_type=self._classify_import(module),
                            )
                            file_imports.append(import_stmt)
                            total_imports += 1

                import_analysis[str(file_path)] = file_imports

                # Check for consolidation candidates
                for target_name, target_config in self.config[
                    "consolidation_targets"
                ].items():
                    if target_name not in consolidation_candidates:
                        consolidation_candidates[target_name] = {
                            "target_file": target_config["target_file"],
                            "priority": target_config["priority"],
                            "risk_level": target_config["risk_level"],
                            "files_using": [],
                            "import_count": 0,
                            "imports": [],
                        }

                    # Check if this file uses imports that could be consolidated
                    for import_stmt in file_imports:
                        if self._is_consolidation_candidate(
                            import_stmt, target_config["imports"]
                        ):
                            consolidation_candidates[target_name]["files_using"].append(
                                str(file_path)
                            )
                            consolidation_candidates[target_name]["import_count"] += 1
                            # Add import statement if not already added
                            if (
                                import_stmt
                                not in consolidation_candidates[target_name]["imports"]
                            ):
                                consolidation_candidates[target_name]["imports"].append(
                                    import_stmt
                                )

            except Exception as e:
                print(f"⚠️  Error analyzing {file_path}: {e}")
                continue

        # Calculate consolidation potential (use unique file count for percentages)
        consolidation_potential = {}
        total_file_count = len(python_files)
        for target_name, candidate in consolidation_candidates.items():
            if candidate["import_count"] > 0:
                unique_files_affected = len(set(candidate["files_using"]))
                occurrence_count = candidate["import_count"]

                consolidation_potential[target_name] = {
                    # Unique files affected (used for % of codebase)
                    "files_affected": unique_files_affected,
                    # Total occurrences across files
                    "occurrence_count": occurrence_count,
                    # Keep original field name for backward compatibility
                    "import_count": occurrence_count,
                    # Simple heuristic for potential reduction
                    "potential_reduction": occurrence_count * 0.7,
                    "risk_level": candidate["risk_level"],
                    "priority": candidate["priority"],
                    # Convenience metric
                    "percent_of_codebase": (
                        (unique_files_affected / total_file_count) * 100.0
                        if total_file_count
                        else 0.0
                    ),
                }

        analysis_result = {
            "total_files": len(python_files),
            "total_imports": total_imports,
            "consolidation_candidates": consolidation_candidates,
            "consolidation_potential": consolidation_potential,
            "recommendations": self._generate_consolidation_recommendations(
                consolidation_potential
            ),
        }

        # Convert ImportStatement objects to dictionaries for JSON serialization
        serializable_result = analysis_result.copy()
        for candidate in serializable_result["consolidation_candidates"].values():
            candidate["imports"] = [
                {
                    "module": imp.module,
                    "names": imp.names,
                    "alias": imp.alias,
                    "line_number": imp.line_number,
                    "file_path": str(imp.file_path) if imp.file_path else None,
                    "import_type": imp.import_type.value,
                }
                for imp in candidate["imports"]
            ]

        # Save analysis
        analysis_file = self.root / ".ai_onboard" / "consolidation_analysis.json"
        write_json(analysis_file, serializable_result)

        print(
            f"✅ Analysis complete: {len(python_files)} files, {total_imports} imports"
        )
        print(f"📊 Found {len(consolidation_potential)} consolidation opportunities")

        return analysis_result

    def _classify_import(self, module: str) -> ImportType:
        """Classify import type for consolidation targeting."""
        if module in [
            "pathlib",
            "typing",
            "dataclasses",
            "collections",
            "contextlib",
            "datetime",
            "enum",
            "json",
            "os",
            "sys",
        ]:
            return ImportType.STDLIB
        elif module.startswith("typing."):
            return ImportType.TYPING
        elif module.startswith("pathlib."):
            return ImportType.PATHLIB
        elif module.startswith("dataclasses."):
            return ImportType.DATACLASSES
        elif module in ["fastapi", "pydantic", "requests", "yaml"]:
            return ImportType.THIRD_PARTY
        else:
            return ImportType.OTHER

    def _is_consolidation_candidate(
        self, import_stmt: ImportStatement, target_imports: List[str]
    ) -> bool:
        """Check if import statement is a candidate for consolidation."""
        for target_import in target_imports:
            if target_import in import_stmt.module or any(
                target_import in name for name in import_stmt.names
            ):
                return True
        return False

    def _generate_consolidation_recommendations(
        self, consolidation_potential: Dict[str, Any]
    ) -> List[str]:
        """Generate consolidation recommendations based on analysis."""
        recommendations = []

        # Sort by potential impact
        sorted_targets = sorted(
            consolidation_potential.items(),
            key=lambda x: x[1]["potential_reduction"],
            reverse=True,
        )

        for target_name, potential in sorted_targets:
            if (
                potential["potential_reduction"] > 10
            ):  # Only recommend if significant impact
                recommendations.append(
                    f"HIGH IMPACT: {target_name} - {potential['files_affected']} files, "
                    f"{potential['import_count']} imports, {potential['potential_reduction']:.0f} reduction potential"
                )

        return recommendations

    def create_migration_plan(self, target_names: List[str]) -> MigrationPlan:
        """Create a comprehensive migration plan for specified targets."""
        print(f"📋 Creating migration plan for targets: {', '.join(target_names)}")

        # Validate targets exist in config
        valid_targets = []
        for target_name in target_names:
            if target_name in self.config["consolidation_targets"]:
                valid_targets.append(target_name)
            else:
                print(f"⚠️  Target '{target_name}' not found in configuration")

        if not valid_targets:
            raise ValueError("No valid consolidation targets specified")

        # Analyze imports to populate consolidation targets
        import_analysis = self.analyze_consolidation_opportunities()

        # Create consolidation targets with actual imports
        targets = []
        for target_name in valid_targets:
            target_config = self.config["consolidation_targets"][target_name]

            # Get imports for this target from analysis
            target_imports = []
            if target_name in import_analysis.get("consolidation_candidates", {}):
                candidate = import_analysis["consolidation_candidates"][target_name]
                import_data = candidate.get("imports", [])

                # Convert dictionary imports back to ImportStatement objects
                for imp_data in import_data:
                    if isinstance(imp_data, dict):
                        import_stmt = ImportStatement(
                            module=imp_data["module"],
                            names=imp_data["names"],
                            alias=imp_data["alias"],
                            line_number=imp_data["line_number"],
                            file_path=(
                                Path(imp_data["file_path"])
                                if imp_data["file_path"]
                                else None
                            ),
                            import_type=ImportType(imp_data["import_type"]),
                        )
                        target_imports.append(import_stmt)
                    else:
                        # Already an ImportStatement object
                        target_imports.append(imp_data)

            target = ConsolidationTarget(
                name=target_name,
                imports=target_imports,
                target_file=Path(target_config["target_file"]),
                priority=target_config["priority"],
                risk_level=target_config["risk_level"],
            )
            targets.append(target)

        # Create backup using safety framework
        backup_operation = CleanupOperation(
            operation_type="import_consolidation_backup",
            targets=[],
            description="Backup before import consolidation migration",
        )

        # Execute backup through safety gates
        success, backup_id = self.safety_framework.execute_cleanup_operation(
            backup_operation
        )
        if not success:
            raise Exception(f"Failed to create backup: {backup_id}")

        # Create migration plan
        migration_plan = MigrationPlan(
            targets=targets,
            backup_id=backup_id,
            validation_checks=self.config["safety_checks"],
            rollback_plan=self._create_rollback_plan(targets),
            estimated_duration=len(targets) * 5,  # 5 minutes per target
            risk_assessment=self._assess_migration_risk(targets),
        )

        self.current_migration = migration_plan

        # Save migration plan
        plan_file = self.root / ".ai_onboard" / "migration_plan.json"
        plan_dict = {
            "targets": [
                {
                    "name": target.name,
                    "target_file": str(target.target_file),
                    "priority": target.priority,
                    "risk_level": target.risk_level,
                    "imports": [
                        {
                            "module": imp.module,
                            "names": imp.names,
                            "alias": imp.alias,
                            "line_number": imp.line_number,
                            "file_path": str(imp.file_path) if imp.file_path else None,
                            "import_type": imp.import_type.value,
                        }
                        for imp in target.imports
                    ],
                }
                for target in migration_plan.targets
            ],
            "backup_id": migration_plan.backup_id,
            "validation_checks": migration_plan.validation_checks,
            "rollback_plan": migration_plan.rollback_plan,
            "estimated_duration": migration_plan.estimated_duration,
            "risk_assessment": migration_plan.risk_assessment,
        }
        write_json(plan_file, plan_dict)

        print(f"✅ Migration plan created with backup ID: {backup_id}")
        print(f"📊 Risk assessment: {migration_plan.risk_assessment['overall_risk']}")

        return migration_plan

    def _create_rollback_plan(
        self, targets: List[ConsolidationTarget]
    ) -> Dict[str, Any]:
        """Create rollback plan for migration targets."""
        rollback_plan = {
            "backup_id": None,  # Will be set during execution
            "target_files": [str(target.target_file) for target in targets],
            "restore_commands": [],
            "validation_checks": self.config["safety_checks"],
        }

        return rollback_plan

    def _assess_migration_risk(
        self, targets: List[ConsolidationTarget]
    ) -> Dict[str, Any]:
        """Assess migration risk for targets."""
        risk_factors = {
            "file_count": sum(1 for target in targets if target.target_file.exists()),
            "priority_levels": [target.priority for target in targets],
            "risk_levels": [target.risk_level for target in targets],
            "target_complexity": len(targets),
        }

        # Calculate overall risk
        if risk_factors["file_count"] == 0:
            overall_risk = "LOW"
        elif risk_factors["file_count"] < 3:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "HIGH"

        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "mitigation_strategies": [
                "Full backup before migration",
                "Incremental validation after each target",
                "Automatic rollback on failure",
                "Dry run validation first",
            ],
        }

    def execute_migration(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute the migration plan with full safety integration."""
        if not self.current_migration:
            raise ValueError("No migration plan available. Create one first.")

        print(f"🚀 Executing migration {'(DRY RUN)' if dry_run else '(LIVE)'}...")

        migration_results = {
            "status": MigrationStatus.IN_PROGRESS.value,
            "targets_completed": [],
            "targets_failed": [],
            "validation_results": [],
            "rollback_performed": False,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
        }

        try:
            # Execute each target
            for target in self.current_migration.targets:
                print(f"📦 Processing target: {target.name}")

                if dry_run:
                    result = self._execute_target_dry_run(target)
                else:
                    result = self._execute_target_live(target)

                if result["success"]:
                    migration_results["targets_completed"].append(target.name)
                    print(f"✅ {target.name} completed successfully")
                else:
                    migration_results["targets_failed"].append(
                        {"target": target.name, "error": result["error"]}
                    )
                    print(f"❌ {target.name} failed: {result['error']}")

                    # Check if we should rollback
                    if self._should_rollback(migration_results):
                        print("🔄 Initiating rollback due to failure threshold...")
                        self._rollback_migration()
                        migration_results["rollback_performed"] = True
                        break

            # Final validation
            if not dry_run and not migration_results["rollback_performed"]:
                validation_result = self._run_final_validation()
                migration_results["validation_results"].append(validation_result)

                if not validation_result["success"]:
                    print("🔄 Final validation failed, initiating rollback...")
                    self._rollback_migration()
                    migration_results["rollback_performed"] = True

            # Update status
            if migration_results["rollback_performed"]:
                migration_results["status"] = MigrationStatus.ROLLED_BACK.value
            elif migration_results["targets_failed"]:
                migration_results["status"] = MigrationStatus.FAILED.value
            else:
                migration_results["status"] = MigrationStatus.COMPLETED.value

            migration_results["end_time"] = datetime.now().isoformat()

            # Log migration
            self._log_migration(migration_results)

            print(f"🏁 Migration completed with status: {migration_results['status']}")

        except Exception as e:
            migration_results["status"] = MigrationStatus.FAILED.value
            migration_results["error"] = str(e)
            migration_results["end_time"] = datetime.now().isoformat()

            print(f"💥 Migration failed with error: {e}")

            # Attempt rollback
            try:
                self._rollback_migration()
                migration_results["rollback_performed"] = True
            except Exception as rollback_error:
                print(f"💥 Rollback also failed: {rollback_error}")

        return migration_results

    def _execute_target_dry_run(self, target: ConsolidationTarget) -> Dict[str, Any]:
        """Execute dry run for a target."""
        print(f"  🔍 DRY RUN: Would create {target.target_file}")
        print(f"  📊 Would consolidate {len(target.imports)} imports")

        return {
            "success": True,
            "dry_run": True,
            "target_file": str(target.target_file),
            "import_count": len(target.imports),
        }

    def _execute_target_live(self, target: ConsolidationTarget) -> Dict[str, Any]:
        """Execute live migration for a target."""
        try:
            # Create target file if it doesn't exist
            if not target.target_file.exists():
                target.target_file.parent.mkdir(parents=True, exist_ok=True)
                target.target_file.touch()

            # Generate consolidated imports
            consolidated_content = self._generate_consolidated_content(target)

            # Write consolidated file
            with open(target.target_file, "w", encoding="utf-8") as f:
                f.write(consolidated_content)

            # Update import statements in affected files
            self._update_import_statements(target)

            return {
                "success": True,
                "target_file": str(target.target_file),
                "import_count": len(target.imports),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_consolidated_content(self, target: ConsolidationTarget) -> str:
        """Generate content for consolidated import file."""
        content = f'"""Consolidated imports for {target.name}."""\n\n'

        # Group imports by type
        stdlib_imports = []
        typing_imports = []
        other_imports = []

        for import_stmt in target.imports:
            if import_stmt.import_type == ImportType.STDLIB:
                stdlib_imports.append(import_stmt)
            elif import_stmt.import_type == ImportType.TYPING:
                typing_imports.append(import_stmt)
            else:
                other_imports.append(import_stmt)

        # Generate import statements
        if stdlib_imports:
            content += "# Standard library imports\n"
            for import_stmt in stdlib_imports:
                if import_stmt.alias:
                    content += f"from {import_stmt.module} import {', '.join(import_stmt.names)} as {import_stmt.alias}\n"
                else:
                    content += f"from {import_stmt.module} import {', '.join(import_stmt.names)}\n"
            content += "\n"

        if typing_imports:
            content += "# Typing imports\n"
            for import_stmt in typing_imports:
                if import_stmt.alias:
                    content += f"from {import_stmt.module} import {', '.join(import_stmt.names)} as {import_stmt.alias}\n"
                else:
                    content += f"from {import_stmt.module} import {', '.join(import_stmt.names)}\n"
            content += "\n"

        if other_imports:
            content += "# Other imports\n"
            for import_stmt in other_imports:
                if import_stmt.alias:
                    content += f"from {import_stmt.module} import {', '.join(import_stmt.names)} as {import_stmt.alias}\n"
                else:
                    content += f"from {import_stmt.module} import {', '.join(import_stmt.names)}\n"

        return content

    def _update_import_statements(self, target: ConsolidationTarget):
        """Update import statements in affected files to use consolidated imports."""
        # Group imports by file
        import re
        from collections import defaultdict

        file_to_imports: Dict[Path, List[ImportStatement]] = defaultdict(list)
        for imp in target.imports:
            if imp.file_path:
                file_to_imports[Path(imp.file_path)].append(imp)

        for file_path, imports in file_to_imports.items():
            try:
                if not file_path.exists():
                    continue

                original_text = file_path.read_text(encoding="utf-8")
                lines = original_text.splitlines()

                # Determine names to consolidate for this file
                names_to_add: List[str] = []
                for imp in imports:
                    if imp.import_type in {ImportType.STDLIB, ImportType.OTHER}:
                        # Use top-level module name (e.g., json, os, sys)
                        top = (imp.module or "").split(".")[0]
                        if top and top not in names_to_add:
                            names_to_add.append(top)
                    elif imp.import_type in {
                        ImportType.TYPING,
                        ImportType.DATACLASS,
                        ImportType.COLLECTIONS,
                        ImportType.CONTEXTLIB,
                        ImportType.DATETIME,
                        ImportType.ENUM,
                    }:
                        for n in imp.names:
                            if n not in names_to_add:
                                names_to_add.append(n)

                # Remove simple import lines where safe
                to_delete_line_indexes: set = set()
                for imp in imports:
                    idx = (imp.line_number or 0) - 1
                    if 0 <= idx < len(lines):
                        line = lines[idx]
                        stripped = line.strip()
                        # Remove very simple forms only; skip complex ones
                        # Patterns: "import modulename" or "from module import Name"
                        simple_import = re.compile(
                            r"^import\s+([A-Za-z0-9_\.]+)(\s+as\s+\w+)?\s*$"
                        )
                        simple_from = re.compile(
                            r"^from\s+([A-Za-z0-9_\.]+)\s+import\s+([A-Za-z0-9_]+)\s*$"
                        )
                        m_imp = simple_import.match(stripped)
                        m_from = simple_from.match(stripped)
                        if m_imp:
                            mod = m_imp.group(1)
                            if (imp.module or "").startswith(
                                mod
                            ) and "," not in stripped:
                                to_delete_line_indexes.add(idx)
                        elif m_from:
                            mod = m_from.group(1)
                            name = m_from.group(2)
                            if (
                                (imp.module or "") == mod
                                and len(imp.names) == 1
                                and imp.names[0] == name
                            ):
                                to_delete_line_indexes.add(idx)

                if to_delete_line_indexes:
                    new_lines = [
                        l
                        for i, l in enumerate(lines)
                        if i not in to_delete_line_indexes
                    ]
                else:
                    new_lines = lines[:]

                # Merge or add consolidated import line based on target module
                target_module = (
                    target.target_file.with_suffix("").as_posix().replace("/", ".")
                )
                ci_prefix = f"from {target_module} import "
                existing_idx = next(
                    (
                        i
                        for i, l in enumerate(new_lines)
                        if l.strip().startswith(ci_prefix)
                    ),
                    -1,
                )

                if names_to_add:
                    if existing_idx >= 0:
                        # Merge into existing
                        existing = new_lines[existing_idx].strip()[len(ci_prefix) :]
                        existing_names = [
                            e.strip() for e in existing.split(",") if e.strip()
                        ]
                        merged = sorted(set(existing_names + names_to_add))
                        new_lines[existing_idx] = ci_prefix + ", ".join(merged)
                    else:
                        # Insert near top (after module docstring if present)
                        insert_pos = 0
                        # Skip shebang or encoding lines
                        while insert_pos < len(new_lines) and (
                            new_lines[insert_pos].startswith("#")
                            or new_lines[insert_pos].startswith("#!")
                        ):
                            insert_pos += 1
                        # If file starts with a docstring, insert after it
                        if insert_pos < len(new_lines) and new_lines[
                            insert_pos
                        ].lstrip().startswith(('"""', "'''")):
                            quote = '"""' if '"""' in new_lines[insert_pos] else "'''"
                            # advance to the closing docstring
                            j = insert_pos + 1
                            while j < len(new_lines) and quote not in new_lines[j]:
                                j += 1
                            insert_pos = min(j + 1, len(new_lines))
                        new_lines.insert(
                            insert_pos, ci_prefix + ", ".join(sorted(set(names_to_add)))
                        )

                updated_text = "\n".join(new_lines) + (
                    "\n" if new_lines and not new_lines[-1].endswith("\n") else ""
                )
                if updated_text != original_text:
                    file_path.write_text(updated_text, encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to update imports in {file_path}: {e}")

    def _should_rollback(self, migration_results: Dict[str, Any]) -> bool:
        """Determine if rollback should be performed."""
        failure_rate = len(migration_results["targets_failed"]) / len(
            self.current_migration.targets
        )
        return failure_rate > self.config["migration_settings"]["rollback_threshold"]

    def _rollback_migration(self):
        """Rollback the migration using the safety framework."""
        if not self.current_migration:
            return

        print("🔄 Rolling back migration...")

        # Use safety framework rollback
        success, message = self.safety_framework.rollback_operation(
            self.current_migration.backup_id
        )

        if success:
            print(f"✅ Rollback completed: {message}")
        else:
            print(f"❌ Rollback failed: {message}")

    def _run_final_validation(self) -> Dict[str, Any]:
        """Run final validation after migration."""
        print("🧪 Running final validation...")

        try:
            # Run comprehensive validation
            validation_report = self.validator.run_comprehensive_validation()

            return {
                "success": validation_report.system_health_score > 0.8,
                "health_score": validation_report.system_health_score,
                "details": validation_report.summary,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _log_migration(self, migration_results: Dict[str, Any]):
        """Log migration results."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "migration_id": (
                self.current_migration.backup_id if self.current_migration else None
            ),
            "results": migration_results,
        }

        with open(self.migration_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        if not self.current_migration:
            return {"status": "No active migration"}

        return {
            "migration_id": self.current_migration.backup_id,
            "targets": [target.name for target in self.current_migration.targets],
            "risk_assessment": self.current_migration.risk_assessment,
            "estimated_duration": self.current_migration.estimated_duration,
        }


def main():
    """Main CLI interface for import consolidation migrator."""
    import argparse

    parser = argparse.ArgumentParser(description="Import Consolidation Migrator")
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze consolidation opportunities"
    )
    parser.add_argument(
        "--create-plan", nargs="+", help="Create migration plan for targets"
    )
    parser.add_argument("--execute", action="store_true", help="Execute migration plan")
    parser.add_argument(
        "--dry-run", action="store_true", help="Execute in dry-run mode"
    )
    parser.add_argument("--status", action="store_true", help="Show migration status")

    args = parser.parse_args()

    migrator = ImportConsolidationMigrator(args.root)

    if args.analyze:
        result = migrator.analyze_consolidation_opportunities()
        print("\n📊 Consolidation Analysis Results:")
        print(f"Total files: {result['total_files']}")
        print(f"Total imports: {result['total_imports']}")
        print(f"Consolidation opportunities: {len(result['consolidation_potential'])}")

        for rec in result["recommendations"]:
            print(f"  • {rec}")

    elif args.create_plan:
        plan = migrator.create_migration_plan(args.create_plan)
        print(f"\n📋 Migration plan created for: {', '.join(args.create_plan)}")
        print(f"Backup ID: {plan.backup_id}")
        print(f"Risk level: {plan.risk_assessment['overall_risk']}")

    elif args.execute:
        results = migrator.execute_migration(dry_run=args.dry_run)
        print(
            f"\n🏁 Migration completed with status: {results['status'] if isinstance(results['status'], str) else results['status'].value}"
        )
        if results["rollback_performed"]:
            print("🔄 Rollback was performed")

    elif args.status:
        status = migrator.get_migration_status()
        print(f"\n📊 Migration Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
