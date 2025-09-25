"""
Dependency Mapping & Module Analysis Engine

This module provides comprehensive dependency analysis including:
- Import relationship mapping
- Dependency graph construction
- Circular dependency detection
- Module coupling and cohesion analysis
- Usage pattern analysis

Author: AI Assistant
"""

import ast
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ModuleDependency:
    """Represents a dependency relationship between modules."""

    from_module: str
    to_module: str
    import_type: str  # 'direct', 'from', 'relative'
    line_number: int
    imported_items: List[str] = field(default_factory=list)


@dataclass
class ModuleMetrics:
    """Metrics for a single module."""

    name: str
    file_path: str
    lines_of_code: int = 0
    incoming_deps: int = 0
    outgoing_deps: int = 0
    complexity_score: float = 0.0
    cohesion_score: float = 0.0  # How related functions are within module
    coupling_score: float = 0.0  # How dependent on other modules


@dataclass
class DependencyAnalysisResult:
    """Complete dependency analysis result."""

    modules_analyzed: int = 0
    total_dependencies: int = 0
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    reverse_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    module_metrics: Dict[str, ModuleMetrics] = field(default_factory=dict)
    strongly_connected_components: List[List[str]] = field(default_factory=list)
    dependency_depths: Dict[str, int] = field(default_factory=dict)


class DependencyMapper:
    """
    Comprehensive dependency mapping and analysis engine.

    Provides detailed analysis of Python module relationships including:
    - Import dependency graphs
    - Circular dependency detection
    - Module coupling/cohesion metrics
    - Dependency hierarchy analysis
    """

    def __init__(self, root_path: Path, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the dependency mapper.

        Args:
            root_path: Root directory to analyze
            exclude_patterns: List of glob patterns to exclude
        """
        self.root_path = root_path
        self.exclude_patterns = exclude_patterns or [
            "__pycache__",
            "*.pyc",
            ".git",
            ".ai_onboard",
            "build",
            "dist",
            "*.egg-info",
            "node_modules",
            "venv",
            ".venv",
            "env",
            ".env",
        ]

        # Analysis state
        self.module_dependencies: Dict[str, List[ModuleDependency]] = defaultdict(list)
        self.module_to_file: Dict[str, str] = {}
        self.file_to_module: Dict[str, str] = {}

    def analyze_dependencies(self) -> DependencyAnalysisResult:
        """
        Perform comprehensive dependency analysis.

        Returns:
            DependencyAnalysisResult with complete analysis
        """
        print("🔗 Starting comprehensive dependency analysis...")

        # Phase 1: Discover all modules
        print("📦 Phase 1: Discovering modules...")
        python_files = self._find_python_files()
        print(f"   Found {len(python_files)} Python files")

        # Map files to module names
        for file_path in python_files:
            module_name = self._file_to_module_name(file_path)
            self.module_to_file[module_name] = file_path
            self.file_to_module[file_path] = module_name

        print(f"   Mapped to {len(self.module_to_file)} unique modules")

        # Phase 2: Analyze dependencies
        print("🔍 Phase 2: Analyzing import relationships...")
        for file_path in python_files:
            try:
                deps = self._analyze_file_dependencies(file_path)
                module_name = self.file_to_module[file_path]
                self.module_dependencies[module_name].extend(deps)
            except Exception as e:
                print(f"   ⚠️  Error analyzing {file_path}: {e}")

        # Phase 3: Build dependency graph
        print("📊 Phase 3: Building dependency graph...")
        result = self._build_dependency_graph()

        # Phase 4: Detect circular dependencies
        print("🔄 Phase 4: Detecting circular dependencies...")
        result.circular_dependencies = self._detect_circular_dependencies(
            result.dependency_graph
        )

        # Phase 5: Calculate metrics
        print("📈 Phase 5: Calculating module metrics...")
        result.module_metrics = self._calculate_module_metrics(result)

        # Phase 6: Analyze strongly connected components
        print("🔗 Phase 6: Analyzing component structure...")
        result.strongly_connected_components = self._find_strongly_connected_components(
            result.dependency_graph
        )

        # Phase 7: Calculate dependency depths
        print("📏 Phase 7: Calculating dependency depths...")
        result.dependency_depths = self._calculate_dependency_depths(
            result.dependency_graph
        )

        print("✅ Dependency analysis complete!")
        return result

    def _find_python_files(self) -> List[str]:
        """Find all Python files in the codebase."""
        python_files = []

        for root, dirs, files in os.walk(self.root_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]

            for file in files:
                if file.endswith(".py") and not self._is_excluded(
                    os.path.join(root, file)
                ):
                    python_files.append(os.path.join(root, file))

        return python_files

    def _is_excluded(self, path: str) -> bool:
        """Check if a path should be excluded."""
        path_str = str(path)

        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True

            # Handle glob-like patterns
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(
                    os.path.basename(path_str), pattern
                ):
                    return True

        return False

    def _file_to_module_name(self, file_path: str) -> str:
        """Convert file path to module name."""
        # Remove root path
        rel_path = os.path.relpath(file_path, self.root_path)

        # Remove .py extension
        if rel_path.endswith(".py"):
            rel_path = rel_path[:-3]

        # Convert path separators to dots
        module_name = rel_path.replace(os.sep, ".")

        # Handle __init__.py files (they represent the package)
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]  # Remove .__init__

        return module_name

    def _analyze_file_dependencies(self, file_path: str) -> List[ModuleDependency]:
        """Analyze dependencies in a single file."""
        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)
            from_module = self.file_to_module[file_path]

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split(".")[0]
                        if (
                            module_name in self.module_to_file
                            or self._is_standard_module(module_name)
                        ):
                            dependencies.append(
                                ModuleDependency(
                                    from_module=from_module,
                                    to_module=module_name,
                                    import_type="direct",
                                    line_number=(
                                        node.lineno if hasattr(node, "lineno") else 0
                                    ),
                                    imported_items=[alias.name],
                                )
                            )

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split(".")[0]
                        if (
                            module_name in self.module_to_file
                            or self._is_standard_module(module_name)
                        ):
                            imported_items = [alias.name for alias in node.names]
                            dependencies.append(
                                ModuleDependency(
                                    from_module=from_module,
                                    to_module=module_name,
                                    import_type="from",
                                    line_number=(
                                        node.lineno if hasattr(node, "lineno") else 0
                                    ),
                                    imported_items=imported_items,
                                )
                            )

        except SyntaxError:
            pass
        except Exception as e:
            print(f"   ⚠️  Error parsing {file_path}: {e}")

        return dependencies

    def _is_standard_module(self, module_name: str) -> bool:
        """Check if a module is from Python's standard library."""

        # Common standard library modules
        stdlib_modules = {
            "sys",
            "os",
            "re",
            "json",
            "pathlib",
            "collections",
            "itertools",
            "functools",
            "operator",
            "datetime",
            "time",
            "math",
            "random",
            "string",
            "io",
            "typing",
            "enum",
            "dataclasses",
            "abc",
            "ast",
            "inspect",
            "importlib",
            "pkgutil",
            "linecache",
            "pickle",
            "copyreg",
            "copy",
            "pprint",
            "reprlib",
            "enum",
            "numbers",
            "cmath",
            "decimal",
            "fractions",
            "statistics",
            "zlib",
            "gzip",
            "bz2",
            "lzma",
            "zipfile",
            "tarfile",
            "csv",
            "configparser",
            "netrc",
            "xdrlib",
            "plistlib",
            "hashlib",
            "hmac",
            "secrets",
            "ssl",
            "socket",
            "mmap",
            "contextvars",
            "concurrent",
            "threading",
            "multiprocessing",
            "subprocess",
            "sched",
            "queue",
            "_thread",
            "dummy_thread",
            "io",
            "codecs",
            "unicodedata",
            "stringprep",
            "re",
            "difflib",
            "textwrap",
            "unicodedata",
            "stringprep",
            "re",
            "locale",
            "gettext",
            "argparse",
            "optparse",
            "getopt",
            "readline",
            "rlcompleter",
            "shutil",
            "glob",
            "fnmatch",
            "linecache",
            "tokenize",
            "token",
            "keyword",
            "ast",
            "symtable",
            "symbol",
            "tokenize",
            "tabnanny",
            "pyclbr",
            "py_compile",
            "compileall",
            "dis",
            "pickletools",
            "platform",
            "errno",
            "ctypes",
            "msvcrt",
            "winreg",
            "winsound",
            "posix",
            "pwd",
            "spwd",
            "grp",
            "crypt",
            "termios",
            "tty",
            "pty",
            "fcntl",
            "pipes",
            "resource",
            "nis",
            "syslog",
            "optparse",
            "nntplib",
            "poplib",
            "imaplib",
            "smtplib",
            "smtpd",
            "telnetlib",
            "uuid",
            "socketserver",
            "http",
            "ftplib",
            "poplib",
            "imaplib",
            "nntplib",
            "smtplib",
            "smtpd",
            "telnetlib",
            "uuid",
            "urllib",
            "urllib2",
            "urlparse",
            "cookielib",
            "Cookie",
            "BaseHTTPServer",
            "SimpleHTTPServer",
            "CGIHTTPServer",
            "wsgiref",
            "webbrowser",
            "cgi",
            "cgitb",
            "wsgiref",
            "xdrlib",
            "plistlib",
        }

        return module_name in stdlib_modules

    def _build_dependency_graph(self) -> DependencyAnalysisResult:
        """Build the dependency graph from collected dependencies."""
        result = DependencyAnalysisResult()
        result.modules_analyzed = len(self.module_to_file)

        # Build forward dependencies (who this module imports)
        dependency_graph = defaultdict(list)
        reverse_dependencies = defaultdict(list)

        for module, deps in self.module_dependencies.items():
            unique_deps = set()
            for dep in deps:
                if dep.to_module not in unique_deps:
                    dependency_graph[module].append(dep.to_module)
                    reverse_dependencies[dep.to_module].append(module)
                    unique_deps.add(dep.to_module)
                    result.total_dependencies += 1

        result.dependency_graph = dict(dependency_graph)
        result.reverse_dependencies = dict(reverse_dependencies)

        return result

    def _detect_circular_dependencies(
        self, dependency_graph: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Detect circular dependencies in the dependency graph."""
        circular_deps = []

        # Use NetworkX for cycle detection if available
        try:
            import networkx as nx

            G = nx.DiGraph(dependency_graph)
            cycles = list(nx.simple_cycles(G))
            circular_deps = cycles
        except (ImportError, AttributeError):
            # Fallback to simpler cycle detection
            circular_deps = self._simple_cycle_detection(dependency_graph)

        return circular_deps

    def _simple_cycle_detection(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Simple cycle detection using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _calculate_module_metrics(
        self, result: DependencyAnalysisResult
    ) -> Dict[str, ModuleMetrics]:
        """Calculate metrics for each module."""
        metrics = {}

        for module_name in self.module_to_file:
            file_path = self.module_to_file[module_name]

            metric = ModuleMetrics(
                name=module_name,
                file_path=file_path,
                incoming_deps=len(result.reverse_dependencies.get(module_name, [])),
                outgoing_deps=len(result.dependency_graph.get(module_name, [])),
            )

            # Calculate lines of code
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    metric.lines_of_code = len([line for line in lines if line.strip()])
            except:
                pass

            # Calculate coupling score (afferent + efferent coupling)
            metric.coupling_score = metric.incoming_deps + metric.outgoing_deps

            # Calculate cohesion score (simplified - based on function/class ratio)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content)

                functions = sum(
                    1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                )
                classes = sum(
                    1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
                )

                if functions + classes > 0:
                    # Higher cohesion if functions and classes are balanced
                    ratio = (
                        min(functions, classes) / max(functions, classes)
                        if max(functions, classes) > 0
                        else 1
                    )
                    metric.cohesion_score = ratio * 100
            except:
                metric.cohesion_score = 50  # Default

            metrics[module_name] = metric

        return metrics

    def _find_strongly_connected_components(
        self, dependency_graph: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Find strongly connected components in the dependency graph."""
        try:
            import networkx as nx

            G = nx.DiGraph(dependency_graph)
            scc = list(nx.strongly_connected_components(G))
            return [list(component) for component in scc if len(component) > 1]
        except (ImportError, AttributeError):
            # Fallback - return empty list
            return []

    def _calculate_dependency_depths(
        self, dependency_graph: Dict[str, List[str]]
    ) -> Dict[str, int]:
        """Calculate the maximum dependency depth for each module."""
        depths: Dict[str, int] = {}

        def calculate_depth(module: str, visited: Set[str]) -> int:
            if module in visited:
                return 0  # Avoid cycles
            if module in depths:
                return depths[module]

            visited.add(module)
            max_depth = 0

            for dep in dependency_graph.get(module, []):
                depth = calculate_depth(dep, visited) + 1
                max_depth = max(max_depth, depth)

            visited.remove(module)
            depths[module] = max_depth
            return max_depth

        for module in dependency_graph:
            if module not in depths:
                calculate_depth(module, set())

        return depths

    def generate_dependency_report(
        self, result: DependencyAnalysisResult, output_path: Optional[str] = None
    ) -> str:
        """Generate a comprehensive dependency analysis report."""
        report_lines = []

        report_lines.append("=" * 80)
        report_lines.append("🔗 DEPENDENCY ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        report_lines.append("📊 OVERVIEW:")
        report_lines.append(f"   Modules Analyzed: {result.modules_analyzed}")
        report_lines.append(f"   Total Dependencies: {result.total_dependencies}")
        report_lines.append(
            f"   Circular Dependencies: {len(result.circular_dependencies)}"
        )
        report_lines.append("")

        # Most coupled modules
        if result.module_metrics:
            most_coupled = sorted(
                result.module_metrics.items(),
                key=lambda x: x[1].coupling_score,
                reverse=True,
            )[:5]

            report_lines.append("🔗 MOST COUPLED MODULES:")
            for module, metrics in most_coupled:
                report_lines.append(
                    f"   {module}: {metrics.coupling_score} dependencies"
                )
            report_lines.append("")

        # Circular dependencies
        if result.circular_dependencies:
            report_lines.append("🔄 CIRCULAR DEPENDENCIES:")
            for i, cycle in enumerate(
                result.circular_dependencies[:5], 1
            ):  # Show first 5
                report_lines.append(f"   Cycle {i}: {' -> '.join(cycle)}")
            if len(result.circular_dependencies) > 5:
                report_lines.append(
                    f"   ... and {len(result.circular_dependencies) - 5} more"
                )
            report_lines.append("")

        # Dependency depths
        if result.dependency_depths:
            deepest = sorted(
                result.dependency_depths.items(), key=lambda x: x[1], reverse=True
            )[:5]

            report_lines.append("📏 DEEPEST DEPENDENCY CHAINS:")
            for module, depth in deepest:
                report_lines.append(f"   {module}: depth {depth}")
            report_lines.append("")

        # Module health overview
        if result.module_metrics:
            healthy_modules = sum(
                1
                for m in result.module_metrics.values()
                if m.cohesion_score > 70 and m.coupling_score < 10
            )
            problematic_modules = sum(
                1
                for m in result.module_metrics.values()
                if m.coupling_score > 20 or m.cohesion_score < 30
            )

            report_lines.append("🏥 MODULE HEALTH:")
            report_lines.append(f"   Healthy Modules: {healthy_modules}")
            report_lines.append(f"   Problematic Modules: {problematic_modules}")
            report_lines.append("")

        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Dependency report saved to: {output_path}")

        return report


def main():
    """CLI entry point for dependency analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Dependency Mapping & Module Analysis")
    parser.add_argument("--path", default=".", help="Path to analyze")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--exclude", nargs="*", help="Additional patterns to exclude")

    args = parser.parse_args()

    root_path = Path(args.path)
    mapper = DependencyMapper(root_path, args.exclude)

    try:
        result = mapper.analyze_dependencies()
        report = mapper.generate_dependency_report(result, args.output)

        print(report)

    except Exception as e:
        print(f"❌ Error during dependency analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
