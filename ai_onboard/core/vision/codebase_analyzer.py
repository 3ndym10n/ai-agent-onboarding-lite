"""
Codebase Analyzer: Analyze existing project structure for intelligent planning.

This module scans the existing codebase to inform WBS generation and task planning,
making the planning process more adaptive to the actual project structure.
"""

import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..base import utils


class CodebaseAnalyzer:
    """Analyzes existing codebase structure for intelligent planning."""

    def __init__(self, root: Path):
        self.root = root
        self.analysis_cache_path = root / ".ai_onboard" / "codebase_analysis.json"

    def analyze_codebase_structure(self) -> Dict[str, Any]:
        """
        Analyze the existing codebase structure.

        Returns:
            Comprehensive analysis of project structure
        """
        # Check cache first
        cached_analysis = self._load_cached_analysis()
        if cached_analysis:
            return cached_analysis

        analysis = {
            "languages": self._detect_languages(),
            "frameworks": self._detect_frameworks(),
            "modules": self._analyze_modules(),
            "test_coverage": self._analyze_test_coverage(),
            "complexity_score": self._calculate_complexity_score(),
            "file_structure": self._analyze_file_structure(),
            "dependencies": self._analyze_dependencies(),
        }

        # Cache the analysis
        self._save_analysis_cache(analysis)

        return analysis

    def _detect_languages(self) -> List[str]:
        """Detect programming languages used in the project."""
        languages = set()
        extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
        }

        for root_dir, _, files in os.walk(self.root):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in extensions:
                    languages.add(extensions[ext])

        return sorted(list(languages))

    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks and libraries used in the project."""
        frameworks = set()

        # Check for common Python frameworks
        if self._file_exists_with_content(
            "requirements.txt", ["flask", "django", "fastapi"]
        ):
            frameworks.add(
                "flask"
                if "flask" in self._read_file_content("requirements.txt")
                else "django"
            )

        if self._file_exists_with_content("package.json", ["react", "vue", "angular"]):
            frameworks.add("react")  # Simplified - could be more detailed

        # Check for common patterns
        if self._directory_exists("src/") or self._directory_exists("lib/"):
            frameworks.add("structured_project")

        return sorted(list(frameworks))

    def _analyze_modules(self) -> List[str]:
        """Analyze project modules and components."""
        modules = []

        # Look for Python packages
        for path in self.root.rglob("*.py"):
            if path.parent.name != "__pycache__":
                module_path = str(path.relative_to(self.root))
                if module_path.count("/") <= 2:  # Top-level modules only
                    module_name = module_path.replace("/", ".").replace(".py", "")
                    if module_name not in ["setup", "test", "conftest"]:
                        modules.append(module_name)

        # Look for JavaScript/TypeScript modules
        for path in self.root.rglob("*.js"):
            if not any(x in str(path) for x in ["node_modules", "dist", "build"]):
                module_name = (
                    str(path.relative_to(self.root))
                    .replace("/", ".")
                    .replace(".js", "")
                )
                modules.append(module_name)

        return sorted(list(set(modules)))[:20]  # Limit to top 20

    def _analyze_test_coverage(self) -> float:
        """Analyze test coverage based on file patterns."""
        total_files = 0
        test_files = 0

        for root_dir, _, files in os.walk(self.root):
            # Skip common directories
            if any(
                skip in root_dir
                for skip in [".git", "__pycache__", "node_modules", "dist", "build"]
            ):
                continue

            for file in files:
                total_files += 1
                if any(
                    test_pattern in file.lower()
                    for test_pattern in ["test_", "_test", ".test.", ".spec."]
                ):
                    test_files += 1

        return (test_files / total_files * 100) if total_files > 0 else 0.0

    def _calculate_complexity_score(self) -> float:
        """Calculate a complexity score based on project characteristics."""
        score = 0.0

        # Language complexity
        languages = self._detect_languages()
        if "python" in languages:
            score += 0.3
        if "typescript" in languages:
            score += 0.2
        if "javascript" in languages:
            score += 0.1

        # Framework complexity
        frameworks = self._detect_frameworks()
        if "react" in frameworks:
            score += 0.2
        if "django" in frameworks:
            score += 0.3

        # Module count
        modules = self._analyze_modules()
        score += min(len(modules) * 0.1, 1.0)

        # Test coverage
        test_coverage = self._analyze_test_coverage()
        score += test_coverage / 100 * 0.2

        return min(score, 1.0)

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze the overall file structure."""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "max_depth": 0,
            "avg_files_per_directory": 0.0,
        }

        for root_dir, dirs, files in os.walk(self.root):
            structure["total_directories"] += len(dirs)
            structure["total_files"] += len(files)

            depth = len(Path(root_dir).relative_to(self.root).parts)
            structure["max_depth"] = max(structure["max_depth"], depth)

        if structure["total_directories"] > 0:
            structure["avg_files_per_directory"] = (
                structure["total_files"] / structure["total_directories"]
            )

        return structure

    def _analyze_dependencies(self) -> List[str]:
        """Analyze external dependencies."""
        dependencies = []

        # Check Python requirements
        if (self.root / "requirements.txt").exists():
            try:
                with open(self.root / "requirements.txt", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            dep = (
                                line.split(">=")[0]
                                .split("==")[0]
                                .split("~=")[0]
                                .strip()
                            )
                            if dep not in ["pip", "setuptools", "wheel"]:
                                dependencies.append(f"python:{dep}")
            except Exception:
                pass

        # Check package.json
        if (self.root / "package.json").exists():
            try:
                import json

                with open(self.root / "package.json", "r") as f:
                    package_data = json.load(f)
                    deps = package_data.get("dependencies", {})
                    for dep in deps.keys():
                        dependencies.append(f"node:{dep}")
            except Exception:
                pass

        return sorted(dependencies)[:20]  # Limit to top 20

    def _file_exists_with_content(self, filename: str, keywords: List[str]) -> bool:
        """Check if a file exists and contains any of the keywords."""
        file_path = self.root / filename
        if not file_path.exists():
            return False

        try:
            content = self._read_file_content(filename).lower()
            return any(keyword.lower() in content for keyword in keywords)
        except Exception:
            return False

    def _read_file_content(self, filename: str) -> str:
        """Read file content safely."""
        try:
            with open(self.root / filename, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def _directory_exists(self, dirname: str) -> bool:
        """Check if a directory exists."""
        return (self.root / dirname).is_dir()

    def _load_cached_analysis(self) -> Optional[Dict[str, Any]]:
        """Load cached analysis if it exists and is recent."""
        if not self.analysis_cache_path.exists():
            return None

        try:
            cached_data = utils.read_json(self.analysis_cache_path)
            cache_time = cached_data.get("cached_at")
            if cache_time:
                # Consider cache valid for 24 hours
                from datetime import datetime, timedelta

                cache_datetime = datetime.fromisoformat(
                    cache_time.replace("Z", "+00:00")
                )
                if datetime.now(cache_datetime.tzinfo) - cache_datetime < timedelta(
                    hours=24
                ):
                    analysis_data = cached_data.get("analysis")
                    return analysis_data if isinstance(analysis_data, dict) else None
        except Exception:
            pass

        return None

    def _save_analysis_cache(self, analysis: Dict[str, Any]) -> None:
        """Save analysis to cache."""
        cache_data = {
            "cached_at": utils.now_iso(),
            "analysis": analysis,
        }
        utils.write_json(self.analysis_cache_path, cache_data)


def analyze_codebase_structure(root: Path) -> Dict[str, Any]:
    """
    Convenience function to analyze codebase structure.

    Args:
        root: Project root directory

    Returns:
        Codebase analysis data
    """
    analyzer = CodebaseAnalyzer(root)
    return analyzer.analyze_codebase_structure()
