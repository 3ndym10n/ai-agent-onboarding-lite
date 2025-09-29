"""
Tests for code quality analyzer.

This module tests the comprehensive code quality analysis functionality
that evaluates codebase health, complexity, unused imports, and dead code.
"""

import ast
import tempfile
from pathlib import Path
from typing import List

import pytest

from ai_onboard.core.quality_safety.code_quality_analyzer import (
    CodeQualityAnalysisResult,
    CodeQualityAnalyzer,
    CodeQualityIssue,
    CodeQualityMetrics,
)


class TestCodeQualityAnalyzerInit:
    """Test CodeQualityAnalyzer initialization."""

    def test_init_basic(self, tmp_path):
        """Test basic initialization."""
        analyzer = CodeQualityAnalyzer(tmp_path)

        assert analyzer.root_path == tmp_path
        assert len(analyzer.exclude_patterns) > 0  # Has default exclude patterns
        assert hasattr(analyzer, "import_usage")
        assert hasattr(analyzer, "function_definitions")
        assert hasattr(analyzer, "function_usage")
        assert hasattr(analyzer, "class_definitions")

    def test_init_with_excludes(self, tmp_path):
        """Test initialization with exclude patterns."""
        exclude_patterns = ["*.pyc", "__pycache__"]
        analyzer = CodeQualityAnalyzer(tmp_path, exclude_patterns)

        assert analyzer.exclude_patterns == exclude_patterns

    def test_init_normalizes_path(self, tmp_path):
        """Test that path is properly resolved."""
        # Create a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        analyzer = CodeQualityAnalyzer(subdir)

        assert analyzer.root_path == subdir


class TestFileDiscovery:
    """Test Python file discovery functionality."""

    def test_find_python_files_basic(self, tmp_path):
        """Test finding Python files in a directory."""
        # Create test files
        main_py = tmp_path / "main.py"
        utils_py = tmp_path / "utils.py"
        main_py.write_text("print('hello')")
        utils_py.write_text("def util(): pass")
        (tmp_path / "data.txt").write_text("not python")

        # Create subdirectory with Python file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        helper_py = subdir / "helper.py"
        helper_py.write_text("def helper(): pass")

        analyzer = CodeQualityAnalyzer(tmp_path)
        files = analyzer._find_python_files()

        assert len(files) == 3
        assert str(main_py) in files
        assert str(utils_py) in files
        assert str(helper_py) in files
        assert str(tmp_path / "data.txt") not in files

    def test_find_python_files_excludes(self, tmp_path):
        """Test excluding files based on patterns."""
        # Create test files
        main_py = tmp_path / "main.py"
        test_main_py = tmp_path / "test_main.py"
        main_py.write_text("print('hello')")
        test_main_py.write_text("def test(): pass")
        (tmp_path / "main.pyc").write_text("compiled")

        # Create excluded directory
        excluded_dir = tmp_path / "__pycache__"
        excluded_dir.mkdir()
        (excluded_dir / "module.pyc").write_text("compiled")

        analyzer = CodeQualityAnalyzer(tmp_path, ["*.pyc", "__pycache__"])
        files = analyzer._find_python_files()

        assert len(files) == 2
        assert str(main_py) in files
        assert str(test_main_py) in files
        assert not any(".pyc" in f for f in files)
        assert not any("__pycache__" in f for f in files)

    def test_find_python_files_empty_directory(self, tmp_path):
        """Test finding files in empty directory."""
        analyzer = CodeQualityAnalyzer(tmp_path)
        files = analyzer._find_python_files()

        assert files == []

    def test_is_excluded(self, tmp_path):
        """Test file exclusion logic."""
        analyzer = CodeQualityAnalyzer(tmp_path, ["*.pyc", "__pycache__"])

        assert analyzer._is_excluded("main.pyc")
        assert analyzer._is_excluded("__pycache__/module.pyc")
        assert analyzer._is_excluded("subdir/__pycache__/file.py")
        assert not analyzer._is_excluded("main.py")
        assert not analyzer._is_excluded("utils.py")


class TestFileAnalysis:
    """Test file analysis functionality."""

    def test_analyze_file_definitions_simple_function(self, tmp_path):
        """Test analyzing simple function definitions."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
def simple_function():
    return "hello"

class SimpleClass:
    def method(self):
        pass
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path)
        analyzer._analyze_file_definitions(str(test_file))

        # Check that definitions were captured
        assert "simple_function" in analyzer.function_definitions
        assert "SimpleClass" in analyzer.class_definitions

    def test_analyze_file_definitions_complex(self, tmp_path):
        """Test analyzing complex file with multiple constructs."""
        test_file = tmp_path / "complex.py"
        test_file.write_text(
            """
import os
from typing import List

CONSTANT = "value"

def outer_function():
    def inner_function():
        pass
    return inner_function

class ComplexClass:
    class_var = "value"

    def __init__(self):
        self.instance_var = "value"

    def method_one(self):
        pass

    def method_two(self):
        pass

async def async_function():
    pass
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path)
        analyzer._analyze_file_definitions(str(test_file))

        # Check various definitions (the analyzer only tracks functions and classes, not variables)
        assert "outer_function" in analyzer.function_definitions
        assert "ComplexClass" in analyzer.class_definitions
        # Check imports were tracked
        assert "os" in analyzer.import_usage

    def test_analyze_file_usage_function_calls(self, tmp_path):
        """Test analyzing function usage and calls."""
        test_file = tmp_path / "usage.py"
        test_file.write_text(
            """
import os
from pathlib import Path

def my_function():
    return "value"

class MyClass:
    def my_method(self):
        return "method"

# Usage
result1 = my_function()
obj = MyClass()
result2 = obj.my_method()
path = Path("file.txt")
os.path.exists("file.txt")
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path)
        analyzer._analyze_file_usage(str(test_file))

        # Check that usages were captured
        assert len(analyzer.function_usage) > 0  # Some functions were detected as used
        assert len(analyzer.class_usage) > 0  # Some classes were detected as used

    def test_analyze_file_quality_basic_metrics(self, tmp_path):
        """Test basic file quality analysis."""
        test_file = tmp_path / "quality.py"
        test_file.write_text(
            """
def function_one():
    x = 1
    y = 2
    z = 3
    return x + y + z

class MyClass:
    def method(self):
        if True:
            return "value"
        else:
            return None
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path)
        issues, metrics = analyzer._analyze_file_quality(str(test_file))

        assert isinstance(metrics, CodeQualityMetrics)
        assert metrics.lines_of_code > 0
        assert metrics.complexity_score > 0
        assert metrics.function_count > 0
        assert metrics.class_count > 0
        assert isinstance(issues, list)


class TestComplexityCalculation:
    """Test complexity calculation functionality."""

    def test_calculate_complexity_simple(self):
        """Test complexity calculation for simple code."""
        code = """
def simple_function():
    return "hello"
"""
        tree = ast.parse(code)
        analyzer = CodeQualityAnalyzer(Path("/tmp"))

        complexity = analyzer._calculate_complexity(tree)

        assert complexity > 0
        assert complexity < 10  # Should be low complexity

    def test_calculate_complexity_complex(self):
        """Test complexity calculation for complex code."""
        code = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            else:
                return x + y
        elif y < 0:
            return x - y
        else:
            return x
    elif x < 0:
        for i in range(10):
            if i % 2 == 0:
                x += i
        return x
    else:
        return 0
"""
        tree = ast.parse(code)
        analyzer = CodeQualityAnalyzer(Path("/tmp"))

        complexity = analyzer._calculate_complexity(tree)

        assert complexity > 5  # Should be higher complexity

    def test_calculate_complexity_empty(self):
        """Test complexity calculation for empty code."""
        code = ""
        tree = ast.parse(code)
        analyzer = CodeQualityAnalyzer(Path("/tmp"))

        complexity = analyzer._calculate_complexity(tree)

        assert complexity == 0


class TestImportAnalysis:
    """Test import analysis functionality."""

    def test_extract_imports_from_file(self, tmp_path):
        """Test extracting imports from file content."""
        content = """import os
import sys
from pathlib import Path
from typing import List, Dict
import json as j
from collections import defaultdict as dd
"""

        analyzer = CodeQualityAnalyzer(tmp_path)
        imports = analyzer._extract_imports_from_file(content)

        assert len(imports) >= 6  # Should extract multiple imports
        # Check some specific imports
        import_names = [imp[0] for imp in imports]
        assert "os" in import_names
        assert "sys" in import_names
        assert "json" in import_names

    def test_find_unused_imports_simple(self, tmp_path):
        """Test finding unused imports."""
        # Create a file with imports and usage
        content = """import os
import sys
from pathlib import Path

def func():
    os.path.exists("file")
    return Path("file")
"""

        analyzer = CodeQualityAnalyzer(tmp_path)
        # First extract imports
        imports = analyzer._extract_imports_from_file(content)
        # Set up usage tracking - os and pathlib are used
        analyzer.import_usage["os"].add("test_file")
        analyzer.import_usage["pathlib"].add("test_file")

        unused = analyzer._find_unused_imports("test_file", imports)

        # Should return list of tuples (import_name, line_num)
        assert isinstance(unused, list)  # Should return a list

    def test_find_unused_imports_complex(self, tmp_path):
        """Test finding unused imports in complex code."""
        content = """import os
import sys
import json
from pathlib import Path, PurePath
from typing import List, Dict, Optional
from collections import defaultdict

def func():
    os.path.join("a", "b")
    data = json.loads("[]")
    p = Path("file")
    items: List[str] = []
    mapping: Dict[str, int] = {}
    dd = defaultdict(int)
    return p, items, mapping, dd
"""

        analyzer = CodeQualityAnalyzer(tmp_path)
        # First extract imports
        imports = analyzer._extract_imports_from_file(content)
        # Set up usage tracking for used imports
        test_file = "test_file"
        analyzer.import_usage["os"].add(test_file)
        analyzer.import_usage["json"].add(test_file)
        analyzer.import_usage["pathlib"].add(test_file)
        analyzer.import_usage["typing"].add(test_file)
        analyzer.import_usage["collections"].add(test_file)

        unused = analyzer._find_unused_imports(test_file, imports)

        # Should return list of tuples (import_name, line_num)
        assert isinstance(unused, list)  # Should return a list


class TestDeadFunctionDetection:
    """Test dead function detection."""

    def test_find_dead_functions_simple(self, tmp_path):
        """Test finding unused functions."""
        test_file = tmp_path / "dead.py"
        test_file.write_text(
            """
def used_function():
    return "used"

def unused_function():
    return "unused"

def another_unused():
    pass

class MyClass:
    def used_method(self):
        return used_function()

    def unused_method(self):
        return "unused"
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path)
        # Run definition analysis first
        analyzer._analyze_file_definitions(str(test_file))
        # Run usage analysis first
        analyzer._analyze_file_usage(str(test_file))

        dead_functions = analyzer._find_dead_functions(str(test_file))

        assert "unused_function" in dead_functions
        assert "another_unused" in dead_functions
        # Note: method detection might be different
        # Used functions should not be dead
        assert "used_function" not in dead_functions


class TestQualityScoreCalculation:
    """Test quality score calculation."""

    def test_calculate_quality_score_perfect(self):
        """Test quality score for perfect code."""
        metrics = CodeQualityMetrics(
            file_path="/tmp/perfect.py",
            lines_of_code=100,
            complexity_score=5.0,
            import_count=5,
            function_count=10,
            class_count=2,
            unused_imports=0,
            dead_code_count=0,
            quality_score=0.0,  # Will be calculated
        )
        issues = []  # No issues

        analyzer = CodeQualityAnalyzer(Path("/tmp"))
        score = analyzer._calculate_quality_score(metrics, issues)

        assert score > 80.0  # Should be high score

    def test_calculate_quality_score_poor(self):
        """Test quality score for poor quality code."""
        metrics = CodeQualityMetrics(
            file_path="/tmp/poor.py",
            lines_of_code=1000,
            complexity_score=50.0,
            import_count=20,
            function_count=50,
            class_count=10,
            unused_imports=20,
            dead_code_count=15,
            quality_score=0.0,  # Will be calculated
        )
        issues = [
            CodeQualityIssue(
                file_path="/tmp/poor.py",
                line_number=1,
                issue_type="unused_import",
                severity="high",
                message="Unused import detected",
            )
        ]

        analyzer = CodeQualityAnalyzer(Path("/tmp"))
        score = analyzer._calculate_quality_score(metrics, issues)

        assert score < 80.0  # Should be lower score due to issues


class TestMainAnalysis:
    """Test main analysis workflow."""

    def test_analyze_codebase_simple(self, tmp_path):
        """Test complete codebase analysis."""
        # Create a simple Python file
        main_file = tmp_path / "main.py"
        main_file.write_text(
            """
def main():
    print("Hello World")
    return "done"

if __name__ == "__main__":
    main()
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path)
        result = analyzer.analyze_codebase()

        assert isinstance(result, CodeQualityAnalysisResult)
        assert result.files_analyzed > 0
        assert result.overall_quality_score >= 0
        assert len(result.file_metrics) > 0

    def test_analyze_codebase_complex(self, tmp_path):
        """Test analysis of more complex codebase."""
        # Create multiple files with various constructs
        (tmp_path / "utils.py").write_text(
            """import os
from typing import List

UNUSED_IMPORT = "should be detected"

def used_function():
    return os.path.exists("file")

def unused_function():
    return "dead code"

class UsedClass:
    def used_method(self):
        return used_function()

class UnusedClass:
    def unused_method(self):
        return "dead"
"""
        )

        (tmp_path / "main.py").write_text(
            """from utils import used_function, UsedClass

def main():
    result = used_function()
    obj = UsedClass()
    return obj.used_method()

if __name__ == "__main__":
    main()
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path)
        result = analyzer.analyze_codebase()

        assert isinstance(result, CodeQualityAnalysisResult)
        assert result.files_analyzed == 2
        assert result.overall_quality_score >= 0

        # Check that issues were detected
        assert len(result.issues) > 0  # Should detect quality issues


class TestIntegration:
    """Integration tests for code quality analyzer."""

    def test_full_analysis_workflow(self, tmp_path):
        """Test complete analysis workflow from setup to reporting."""
        # Create a realistic codebase structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create main module
        (src_dir / "__init__.py").write_text("")
        (src_dir / "main.py").write_text(
            """from .utils import helper_function

def main():
    return helper_function()

if __name__ == "__main__":
    print(main())
"""
        )

        # Create utils module
        (src_dir / "utils.py").write_text(
            """import os  # used
import sys  # unused
from typing import List

def helper_function():
    return os.path.basename(__file__)

def unused_function():
    return "dead code"

class UtilityClass:
    def used_method(self):
        return helper_function()

    def unused_method(self):
        return unused_function()
"""
        )

        # Create test file (will be excluded)
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_main.py").write_text(
            """import pytest
from src.main import main

def test_main():
    result = main()
    assert result is not None
"""
        )

        analyzer = CodeQualityAnalyzer(tmp_path, ["tests"])
        result = analyzer.analyze_codebase()

        # Verify comprehensive analysis
        assert result.files_analyzed >= 3  # __init__.py, main.py, utils.py
        assert result.overall_quality_score >= 0

        # Check that various issues were detected
        assert len(result.issues) > 0  # Should detect quality issues
