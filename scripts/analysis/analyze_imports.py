#!/usr/bin/env python3
"""
Import Analysis Script for ai-onboard-lite
Analyzes Python files to identify unused imports and consolidation opportunities.
"""
import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List



class ImportAnalyzer:
    """Analyze imports in Python codebase."""

    def __init__(self, root_path: Path):
        """Initialize the analyzer."""
        self.root_path = root_path
        self.files_analyzed = 0
        self.total_imports = 0
        self.syntax_errors = []
        self.import_stats = defaultdict(int)
        self.module_usage = defaultdict(set)

    def analyze_codebase(self) -> Dict:
        """Analyze all Python files in the codebase."""
        print("Starting comprehensive import analysis...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            self._analyze_file(py_file)

        return self._generate_report()

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = ["venv", "__pycache__", ".git", "node_modules"]
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            self.files_analyzed += 1

            imports = self._extract_imports(tree)
            self.total_imports += len(imports)

            # Count import types
            for imp in imports:
                self.import_stats[imp["type"]] += 1

                # Track module usage
                if imp["type"] == "import_from":
                    self.module_usage[imp["module"]].add(str(file_path))

        except SyntaxError as e:
            self.syntax_errors.append(
                {
                    "file": str(file_path),
                    "error": f"Syntax error: {e.msg} at line {e.lineno}",
                }
            )
        except Exception as e:
            self.syntax_errors.append({"file": str(file_path), "error": str(e)})

    def _extract_imports(self, tree: ast.AST) -> List[Dict]:
        """Extract import statements from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "as_name": alias.asname,
                            "lineno": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import_from",
                            "module": node.module or "",
                            "name": alias.name,
                            "as_name": alias.asname,
                            "lineno": node.lineno,
                        }
                    )

        return imports

    def _generate_report(self) -> Dict:
        """Generate comprehensive analysis report."""
        return {
            "summary": {
                "files_analyzed": self.files_analyzed,
                "total_imports": self.total_imports,
                "average_imports_per_file": (
                    round(self.total_imports / self.files_analyzed, 1)
                    if self.files_analyzed > 0
                    else 0
                ),
                "syntax_errors_count": len(self.syntax_errors),
                "unique_modules_used": len(self.module_usage),
            },
            "import_types": dict(self.import_stats),
            "most_used_modules": sorted(
                [(module, len(files)) for module, files in self.module_usage.items()],
                key=lambda x: x[1],
                reverse=True,
            )[:20],
            "syntax_errors": self.syntax_errors[:10],  # Show first 10
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        avg_imports = (
            self.total_imports / self.files_analyzed if self.files_analyzed > 0 else 0
        )

        if avg_imports > 15:
            recommendations.append(
                "HIGH: Average imports per file is very high ({:.1f}). Consider consolidating imports.".format(
                    avg_imports
                )
            )
        elif avg_imports > 10:
            recommendations.append(
                "MEDIUM: Average imports per file is elevated ({:.1f}). Review for consolidation opportunities.".format(
                    avg_imports
                )
            )

        # Add specific consolidation recommendations
        recommendations.extend(self._get_consolidation_recommendations())

        if self.syntax_errors:
            recommendations.append(
                f"CRITICAL: {len(self.syntax_errors)} files have syntax errors preventing import analysis."
            )

        # Check for commonly unused imports
        std_lib_modules = {
            "os",
            "sys",
            "json",
            "re",
            "datetime",
            "pathlib",
            "typing",
            "collections",
            "itertools",
        }
        commonly_unused = []
        for module in self.module_usage:
            if module in std_lib_modules and len(self.module_usage[module]) < 3:
                commonly_unused.append(module)

        if commonly_unused:
            recommendations.append(
                f"Consider reviewing usage of standard library modules: {', '.join(commonly_unused[:5])}"
            )

        return recommendations

    def _get_consolidation_recommendations(self) -> List[str]:
        """Generate specific consolidation recommendations based on import patterns."""
        recommendations = []

        # Get most commonly used modules
        most_used = sorted(
            [(module, len(files)) for module, files in self.module_usage.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Check for common import patterns that could be consolidated
        common_stdlib = [
            "pathlib",
            "typing",
            "dataclasses",
            "datetime",
            "enum",
            "collections",
        ]
        common_stdlib_usage = sum(
            count for module, count in most_used if module in common_stdlib
        )

        if common_stdlib_usage > 100:
            recommendations.append(
                f"CONSOLIDATION: Consider creating a 'common_imports.py' module for frequently used stdlib imports "
                f"({common_stdlib_usage} total usages of common stdlib modules)"
            )

        # Check for typing imports that could be consolidated
        typing_usage = sum(count for module, count in most_used if module == "typing")
        if typing_usage > 50:
            recommendations.append(
                f"CONSOLIDATION: High usage of 'typing' module ({typing_usage} files). "
                f"Consider creating a 'types.py' module with commonly used type aliases"
            )

        # Check for pathlib usage
        pathlib_usage = sum(count for module, count in most_used if module == "pathlib")
        if pathlib_usage > 50:
            recommendations.append(
                f"CONSOLIDATION: High usage of 'pathlib' module ({pathlib_usage} files). "
                f"Consider creating a 'paths.py' utility module with common path operations"
            )

        # Check for dataclasses usage
        dataclasses_usage = sum(
            count for module, count in most_used if module == "dataclasses"
        )
        if dataclasses_usage > 30:
            recommendations.append(
                f"CONSOLIDATION: High usage of 'dataclasses' module ({dataclasses_usage} files). "
                f"Consider creating a 'models.py' module with common data structures"
            )

        return recommendations


def main():
    root_path = Path(__file__).parent.parent
    analyzer = ImportAnalyzer(root_path)
    report = analyzer.analyze_codebase()

    print("\n" + "=" * 60)
    print("IMPORT ANALYSIS REPORT")
    print("=" * 60)

    summary = report["summary"]
    print(f"\nSUMMARY:")
    print(f"   Files analyzed: {summary['files_analyzed']}")
    print(f"   Total imports: {summary['total_imports']}")
    print(f"   Average imports per file: {summary['average_imports_per_file']}")
    print(f"   Syntax errors: {summary['syntax_errors_count']}")
    print(f"   Unique modules: {summary['unique_modules_used']}")

    print(f"\nIMPORT TYPES:")
    for imp_type, count in report["import_types"].items():
        print(f"   {imp_type}: {count}")

    print(f"\nMOST USED MODULES:")
    for module, count in report["most_used_modules"][:10]:
        print(f"   {module}: {count} files")

    if report["syntax_errors"]:
        print(f"\nSYNTAX ERRORS (showing first 5):")
        for error in report["syntax_errors"][:5]:
            print(f"   {error['file']}: {error['error']}")

    print(f"\nRECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"   {rec}")

    print(f"\nAnalysis complete!")


if __name__ == "__main__":
    main()
