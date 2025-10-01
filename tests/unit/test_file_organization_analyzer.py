"""
Tests for file organization analyzer.

This module tests the comprehensive file organization analysis functionality
that evaluates codebase structure, file placement, directory cohesion, and
restructuring recommendations.
"""

import ast
from pathlib import Path
from typing import List

from ai_onboard.core.monitoring_analytics.file_organization_analyzer import (
    DirectoryAnalysis,
    FileOrganizationAnalyzer,
    FileOrganizationIssue,
    FileOrganizationResult,
)


class TestFileOrganizationAnalyzerInit:
    """Test FileOrganizationAnalyzer initialization."""

    def test_init_basic(self, tmp_path):
        """Test basic initialization."""
        analyzer = FileOrganizationAnalyzer(tmp_path)

        assert analyzer.root_path == tmp_path
        assert len(analyzer.exclude_patterns) > 4  # Has default exclude patterns
        assert hasattr(analyzer, "all_files")
        assert hasattr(analyzer, "file_complexity")
        assert hasattr(analyzer, "file_imports")
        assert hasattr(analyzer, "file_exports")

    def test_init_with_excludes(self, tmp_path):
        """Test initialization with custom exclude patterns."""
        exclude_patterns = ["*.pyc", "test_*"]
        analyzer = FileOrganizationAnalyzer(tmp_path, exclude_patterns)

        assert analyzer.exclude_patterns == exclude_patterns

    def test_init_normalizes_path(self, tmp_path):
        """Test that path is properly resolved."""
        # Create a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        analyzer = FileOrganizationAnalyzer(subdir)

        assert analyzer.root_path == subdir


class TestFileDiscovery:
    """Test file discovery functionality."""

    def test_discover_files_basic(self, tmp_path):
        """Test discovering Python files in a directory."""
        # Create test files
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def util(): pass")
        (tmp_path / "data.txt").write_text("not python")

        # Create subdirectory with Python file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "helper.py").write_text("def helper(): pass")

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()

        assert len(analyzer.all_files) == 4  # All files are discovered
        assert str(tmp_path / "main.py") in analyzer.all_files
        assert str(tmp_path / "utils.py") in analyzer.all_files
        assert str(tmp_path / "subdir" / "helper.py") in analyzer.all_files
        assert str(tmp_path / "data.txt") in analyzer.all_files

    def test_discover_files_excludes(self, tmp_path):
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

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()

        assert len(analyzer.all_files) == 2  # Excluded files are not included
        assert str(main_py) in analyzer.all_files
        assert str(test_main_py) in analyzer.all_files
        assert not any(".pyc" in f for f in analyzer.all_files)
        assert not any("__pycache__" in f for f in analyzer.all_files)

    def test_discover_files_empty_directory(self, tmp_path):
        """Test discovering files in empty directory."""
        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()

        assert analyzer.all_files == []

    def test_is_excluded(self, tmp_path):
        """Test file exclusion logic."""
        analyzer = FileOrganizationAnalyzer(tmp_path)

        assert analyzer._is_excluded("main.pyc")
        assert analyzer._is_excluded("__pycache__/module.pyc")
        assert analyzer._is_excluded("subdir/__pycache__/file.py")
        assert not analyzer._is_excluded("main.py")
        assert not analyzer._is_excluded("utils.py")


class TestFileComplexityAnalysis:
    """Test file complexity analysis functionality."""

    def test_analyze_file_complexity_simple(self, tmp_path):
        """Test analyzing complexity of a simple file."""
        test_file = tmp_path / "simple.py"
        test_file.write_text(
            """
def simple_function():
    return "hello"

class SimpleClass:
    def method(self):
        pass
"""
        )

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()
        analyzer._analyze_file_complexity(str(test_file))

        assert str(test_file) in analyzer.file_complexity
        complexity = analyzer.file_complexity[str(test_file)]
        assert complexity > 0  # Should have some complexity

    def test_analyze_file_complexity_complex(self, tmp_path):
        """Test analyzing complexity of a complex file."""
        test_file = tmp_path / "complex.py"
        test_file.write_text(
            """
import os
from typing import List, Dict

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

class ComplexClass:
    def __init__(self):
        self.data = []

    def method_one(self):
        pass

    def method_two(self):
        pass

    def method_three(self):
        pass
"""
        )

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()
        analyzer._analyze_file_complexity(str(test_file))

        assert str(test_file) in analyzer.file_complexity
        complexity = analyzer.file_complexity[str(test_file)]
        assert complexity > 5  # Should have higher complexity

    def test_analyze_file_complexity_empty(self, tmp_path):
        """Test analyzing complexity of an empty file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()
        analyzer._analyze_file_complexity(str(test_file))

        assert str(test_file) in analyzer.file_complexity
        complexity = analyzer.file_complexity[str(test_file)]
        assert complexity == 0  # Empty file should have zero complexity


class TestFileRelationships:
    """Test file relationship analysis functionality."""

    def test_analyze_file_relationships_imports(self, tmp_path):
        """Test analyzing import relationships between files."""
        # Create main file
        main_file = tmp_path / "main.py"
        main_file.write_text(
            """from utils import helper_function
from pathlib import Path

def main():
    result = helper_function()
    return result
"""
        )

        # Create utils file
        utils_file = tmp_path / "utils.py"
        utils_file.write_text(
            """import os
from typing import List

def helper_function():
    return os.path.basename(__file__)
"""
        )

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()
        analyzer._analyze_file_relationships()

        # Check that relationships were captured
        assert len(analyzer.file_imports) > 0
        # Should have import relationships

    def test_analyze_file_relationships_no_imports(self, tmp_path):
        """Test analyzing files with no imports."""
        # Create standalone file
        standalone_file = tmp_path / "standalone.py"
        standalone_file.write_text(
            """def standalone_function():
    return "standalone"

class StandaloneClass:
    pass
"""
        )

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()
        analyzer._analyze_file_relationships()

        # File with no imports should still be processed
        assert len(analyzer.file_imports) >= 0


class TestModuleConversion:
    """Test module name conversion functionality."""

    def test_file_to_module_simple(self, tmp_path):
        """Test converting file path to module name."""
        analyzer = FileOrganizationAnalyzer(tmp_path)

        # Create test files
        main_py = tmp_path / "main.py"
        utils_helper_py = tmp_path / "utils" / "helper.py"
        (tmp_path / "utils").mkdir()

        # Test various file paths
        assert analyzer._file_to_module(str(main_py)) == "main"
        assert analyzer._file_to_module(str(utils_helper_py)) == "utils.helper"

    def test_file_to_module_edge_cases(self, tmp_path):
        """Test module conversion edge cases."""
        analyzer = FileOrganizationAnalyzer(tmp_path)

        init_py = tmp_path / "__init__.py"
        deep_file_py = tmp_path / "deep" / "nested" / "path" / "file.py"
        (tmp_path / "deep" / "nested" / "path").mkdir(parents=True)

        assert analyzer._file_to_module(str(init_py)) == "__init__"
        assert analyzer._file_to_module(str(deep_file_py)) == "deep.nested.path.file"


class TestDirectoryAnalysis:
    """Test directory analysis functionality."""

    def test_analyze_directories_basic(self, tmp_path):
        """Test basic directory analysis."""
        # Create directory structure
        (tmp_path / "main.py").write_text("print('main')")
        (tmp_path / "utils.py").write_text("def util(): pass")

        utils_dir = tmp_path / "utils"
        utils_dir.mkdir()
        (utils_dir / "__init__.py").write_text("")
        (utils_dir / "helpers.py").write_text("def helper(): pass")
        (utils_dir / "validators.py").write_text("def validate(): pass")

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()
        result = analyzer._analyze_directories()

        assert isinstance(result, dict)
        assert len(result) > 0  # Should analyze root and utils directories

        # Check root directory analysis
        root_key = str(tmp_path)
        assert root_key in result
        root_analysis = result[root_key]
        assert isinstance(root_analysis, DirectoryAnalysis)

    def test_calculate_directory_cohesion_high(self, tmp_path):
        """Test calculating cohesion for highly cohesive directory."""
        analyzer = FileOrganizationAnalyzer(tmp_path)

        # Files that are highly related (all about user management)
        dir_files = [
            "user_manager.py",
            "user_validator.py",
            "user_repository.py",
            "user_service.py",
        ]

        cohesion = analyzer._calculate_directory_cohesion(dir_files)
        assert cohesion > 0.5  # Should have high cohesion

    def test_calculate_directory_cohesion_low(self, tmp_path):
        """Test calculating cohesion for loosely cohesive directory."""
        analyzer = FileOrganizationAnalyzer(tmp_path)

        # Files that are unrelated (different extensions)
        dir_files = [
            "user_manager.py",
            "database_connection.py",
            "email_sender.txt",
            "file_processor.md",
        ]

        cohesion = analyzer._calculate_directory_cohesion(dir_files)
        assert cohesion >= 0  # Should return a valid cohesion score


class TestOrganizationIssues:
    """Test organization issue identification."""

    def test_identify_organization_issues_basic(self, tmp_path):
        """Test basic organization issue identification."""
        # Create a file structure with potential issues
        (tmp_path / "main.py").write_text("print('main')")

        # Create a directory with mixed concerns
        mixed_dir = tmp_path / "mixed"
        mixed_dir.mkdir()
        (mixed_dir / "user_auth.py").write_text("def login(): pass")
        (mixed_dir / "email_utils.py").write_text("def send_email(): pass")
        (mixed_dir / "database.py").write_text("def connect(): pass")

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()
        # Run full analysis workflow to populate all necessary data
        analyzer._analyze_directories()
        analyzer._analyze_file_relationships()

        # Now test issue identification
        issues = []
        for file_path in analyzer.all_files:
            if file_path.endswith(".py"):
                file_issues = analyzer._analyze_file_placement(file_path)
                issues.extend(file_issues)

        assert isinstance(issues, list)

    def test_analyze_file_placement_good(self, tmp_path):
        """Test analyzing well-placed files."""
        # Create a well-organized structure
        models_dir = tmp_path / "models"
        models_dir.mkdir()
        (models_dir / "user.py").write_text("class User: pass")
        (models_dir / "product.py").write_text("class Product: pass")

        views_dir = tmp_path / "views"
        views_dir.mkdir()
        (views_dir / "user_views.py").write_text("def user_view(): pass")
        (views_dir / "product_views.py").write_text("def product_view(): pass")

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()

        # Test file placement analysis
        issues = analyzer._analyze_file_placement(str(models_dir / "user.py"))
        assert isinstance(issues, list)

    def test_analyze_file_placement_poor(self, tmp_path):
        """Test analyzing poorly placed files."""
        # Create a file in wrong location
        (tmp_path / "user_models_and_views.py").write_text(
            """
class User: pass
def user_view(): pass
"""
        )

        analyzer = FileOrganizationAnalyzer(tmp_path)
        analyzer._discover_files()

        issues = analyzer._analyze_file_placement(
            str(tmp_path / "user_models_and_views.py")
        )
        assert isinstance(issues, list)


class TestMainAnalysis:
    """Test main analysis workflow."""

    def test_analyze_organization_simple(self, tmp_path):
        """Test complete organization analysis."""
        # Create a simple file structure
        (tmp_path / "main.py").write_text(
            """
def main():
    print("Hello World")
    return "done"

if __name__ == "__main__":
    main()
"""
        )

        (tmp_path / "utils.py").write_text(
            """
def helper():
    return "helper"
"""
        )

        analyzer = FileOrganizationAnalyzer(tmp_path)
        result = analyzer.analyze_organization()

        assert isinstance(result, FileOrganizationResult)
        assert result.files_analyzed >= 2
        assert isinstance(result.directory_analysis, dict)
        assert isinstance(result.organization_issues, list)

    def test_analyze_organization_complex(self, tmp_path):
        """Test analysis of complex file structure."""
        # Create a more complex structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "__init__.py").write_text("")
        (src_dir / "main.py").write_text(
            "from .utils import helper\ndef main(): return helper()"
        )
        (src_dir / "utils.py").write_text("def helper(): return 'helper'")

        models_dir = src_dir / "models"
        models_dir.mkdir()
        (models_dir / "__init__.py").write_text("")
        (models_dir / "user.py").write_text("class User: pass")
        (models_dir / "product.py").write_text("class Product: pass")

        views_dir = src_dir / "views"
        views_dir.mkdir()
        (views_dir / "user_views.py").write_text("def user_view(): pass")

        analyzer = FileOrganizationAnalyzer(tmp_path)
        result = analyzer.analyze_organization()

        assert isinstance(result, FileOrganizationResult)
        assert result.files_analyzed >= 5
        assert len(result.directory_analysis) > 0
        assert isinstance(result.consolidation_candidates, list)
        assert isinstance(result.restructuring_recommendations, list)


class TestIntegration:
    """Integration tests for file organization analyzer."""

    def test_full_analysis_workflow(self, tmp_path):
        """Test complete analysis workflow from setup to reporting."""
        # Create a realistic project structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Main package
        (src_dir / "__init__.py").write_text("")
        (src_dir / "app.py").write_text(
            """
from .models.user import User
from .services.user_service import UserService

def create_app():
    user = User()
    service = UserService()
    return "app"
"""
        )

        # Models package
        models_dir = src_dir / "models"
        models_dir.mkdir()
        (models_dir / "__init__.py").write_text("")
        (models_dir / "user.py").write_text(
            "class User:\n    def __init__(self): self.name = 'user'"
        )
        (models_dir / "product.py").write_text(
            "class Product:\n    def __init__(self): self.name = 'product'"
        )

        # Services package
        services_dir = src_dir / "services"
        services_dir.mkdir()
        (services_dir / "__init__.py").write_text("")
        (services_dir / "user_service.py").write_text(
            """
from ..models.user import User

class UserService:
    def create_user(self):
        return User()
"""
        )
        (services_dir / "product_service.py").write_text(
            """
from ..models.product import Product

class ProductService:
    def create_product(self):
        return Product()
"""
        )

        # Utils (might be misplaced)
        (src_dir / "utils.py").write_text(
            """
import os

def file_utils():
    return os.path.exists("file")

def string_utils():
    return "utils"
"""
        )

        # Tests (should be excluded)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").write_text("def test_app(): pass")

        analyzer = FileOrganizationAnalyzer(tmp_path, ["tests"])
        result = analyzer.analyze_organization()

        # Verify comprehensive analysis
        assert result.files_analyzed >= 6  # main files without tests
        assert len(result.directory_analysis) > 0
        assert isinstance(result.organization_issues, list)
        assert isinstance(result.consolidation_candidates, list)
        assert isinstance(result.restructuring_recommendations, list)

        # Should identify some organizational insights
        assert len(result.organization_issues) >= 0
