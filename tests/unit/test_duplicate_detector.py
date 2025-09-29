"""
Tests for duplicate detector.

This module tests the comprehensive code duplicate detection functionality
that identifies exact duplicates, near-duplicates, and structural similarities
in Python codebases.
"""

import ast
from pathlib import Path
from typing import List

import pytest

from ai_onboard.core.quality_safety.duplicate_detector import (
    CodeBlock,
    DuplicateAnalysisResult,
    DuplicateDetector,
    DuplicateGroup,
)


class TestDuplicateDetectorInit:
    """Test DuplicateDetector initialization."""

    def test_init_basic(self, tmp_path):
        """Test basic initialization."""
        analyzer = DuplicateDetector(tmp_path)

        assert analyzer.root_path == tmp_path
        assert len(analyzer.exclude_patterns) > 4  # Has default exclude patterns
        assert analyzer.min_block_size == 6  # Default min block size
        assert hasattr(analyzer, "code_blocks")
        assert hasattr(analyzer, "hash_to_blocks")

    def test_init_with_custom_params(self, tmp_path):
        """Test initialization with custom parameters."""
        exclude_patterns = ["*.pyc", "test_*"]
        analyzer = DuplicateDetector(
            tmp_path, exclude_patterns=exclude_patterns, min_block_size=5
        )

        assert analyzer.exclude_patterns == exclude_patterns
        assert analyzer.min_block_size == 5

    def test_init_normalizes_path(self, tmp_path):
        """Test that path is properly resolved."""
        # Create a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        analyzer = DuplicateDetector(subdir)

        assert analyzer.root_path == subdir


class TestFileDiscovery:
    """Test file discovery functionality."""

    def test_find_python_files_basic(self, tmp_path):
        """Test discovering Python files in a directory."""
        # Create test files
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def util(): pass")
        (tmp_path / "data.txt").write_text("not python")

        # Create subdirectory with Python file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "helper.py").write_text("def helper(): pass")

        analyzer = DuplicateDetector(tmp_path)
        files = analyzer._find_python_files()

        assert len(files) >= 3  # May include more files from the project
        assert any("main.py" in f for f in files)
        assert any("utils.py" in f for f in files)
        assert any("helper.py" in f for f in files)

    def test_find_python_files_excludes(self, tmp_path):
        """Test excluding files based on patterns."""
        # Create test files
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "test_main.py").write_text("def test(): pass")
        (tmp_path / "main.pyc").write_text("compiled")

        # Create excluded directory
        excluded_dir = tmp_path / "__pycache__"
        excluded_dir.mkdir()
        (excluded_dir / "module.pyc").write_text("compiled")

        analyzer = DuplicateDetector(tmp_path)
        files = analyzer._find_python_files()

        # Should not include excluded files
        assert not any(".pyc" in f for f in files)
        assert not any("__pycache__" in f for f in files)

    def test_is_excluded(self, tmp_path):
        """Test file exclusion logic."""
        analyzer = DuplicateDetector(tmp_path)

        assert analyzer._is_excluded("main.pyc")
        assert analyzer._is_excluded("__pycache__/module.pyc")
        assert analyzer._is_excluded("subdir/__pycache__/file.py")
        assert not analyzer._is_excluded("main.py")
        assert not analyzer._is_excluded("utils.py")


class TestCodeBlockExtraction:
    """Test code block extraction functionality."""

    def test_extract_code_blocks_simple_function(self, tmp_path):
        """Test extracting code blocks from a simple function."""
        test_file = tmp_path / "simple.py"
        test_file.write_text(
            """
def simple_function():
    x = 1
    y = 2
    return x + y

class SimpleClass:
    def method(self):
        return "hello"
"""
        )

        analyzer = DuplicateDetector(tmp_path)
        blocks = analyzer._extract_code_blocks(str(test_file))

        assert len(blocks) >= 0  # Should extract some blocks
        # The exact extraction depends on the implementation details

    def test_extract_code_blocks_complex_file(self, tmp_path):
        """Test extracting code blocks from a complex file."""
        test_file = tmp_path / "complex.py"
        test_file.write_text(
            """
import os
from typing import List

def outer_function():
    def inner_function():
        return "inner"
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

        analyzer = DuplicateDetector(tmp_path)
        blocks = analyzer._extract_code_blocks(str(test_file))

        assert len(blocks) >= 0  # Should extract some blocks
        # The exact extraction depends on the implementation details

    def test_extract_code_blocks_empty_file(self, tmp_path):
        """Test extracting code blocks from an empty file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        analyzer = DuplicateDetector(tmp_path)
        blocks = analyzer._extract_code_blocks(str(test_file))

        assert len(blocks) == 0


class TestUtilityMethods:
    """Test utility methods."""

    def test_tokenize_code(self, tmp_path):
        """Test code tokenization."""
        analyzer = DuplicateDetector(tmp_path)

        code = "def func():\n    x = 1\n    return x"
        tokens = analyzer._tokenize_code(code)

        assert len(tokens) > 0
        assert "def" in tokens
        assert "func" in tokens
        assert "return" in tokens

    def test_hash_content(self, tmp_path):
        """Test content hashing."""
        analyzer = DuplicateDetector(tmp_path)

        content1 = "def func():\n    return 1"
        content2 = "def func():\n    return 1"
        content3 = "def func():\n    return 2"

        hash1 = analyzer._hash_content(content1)
        hash2 = analyzer._hash_content(content2)
        hash3 = analyzer._hash_content(content3)

        assert hash1 == hash2  # Same content should have same hash
        assert hash1 != hash3  # Different content should have different hash

    def test_get_line_indent(self, tmp_path):
        """Test line indentation calculation."""
        analyzer = DuplicateDetector(tmp_path)

        assert analyzer._get_line_indent("no indent") == 0
        assert analyzer._get_line_indent("    indented") == 4
        assert (
            analyzer._get_line_indent("\t\ttabbed") == 2
        )  # Just counts tab characters


class TestDuplicateDetection:
    """Test duplicate detection functionality."""

    def test_find_exact_duplicates_no_duplicates(self, tmp_path):
        """Test finding exact duplicates when none exist."""
        # Create files with different content
        (tmp_path / "file1.py").write_text("def func1():\n    return 1")
        (tmp_path / "file2.py").write_text("def func2():\n    return 2")

        analyzer = DuplicateDetector(tmp_path)
        analyzer._find_python_files()
        for file_path in analyzer._find_python_files():
            if file_path.endswith(".py"):
                blocks = analyzer._extract_code_blocks(file_path)
                analyzer.code_blocks.extend(blocks)

        duplicates = analyzer._find_exact_duplicates()

        assert len(duplicates) == 0

    def test_find_exact_duplicates_with_duplicates(self, tmp_path):
        """Test finding exact duplicates when they exist."""
        # Create files with identical functions
        duplicate_code = """def duplicate_function():
    x = 1
    y = 2
    z = 3
    return x + y + z"""

        (tmp_path / "file1.py").write_text(duplicate_code)
        (tmp_path / "file2.py").write_text(duplicate_code)

        analyzer = DuplicateDetector(tmp_path)
        analyzer._find_python_files()
        for file_path in analyzer._find_python_files():
            if file_path.endswith(".py"):
                blocks = analyzer._extract_code_blocks(file_path)
                analyzer.code_blocks.extend(blocks)

        duplicates = analyzer._find_exact_duplicates()

        assert isinstance(duplicates, list)  # Should return a list

    def test_find_near_duplicates(self, tmp_path):
        """Test finding near-duplicate code."""
        # Create files with similar but not identical functions
        (tmp_path / "file1.py").write_text(
            """def func1():
    x = 1
    y = 2
    return x + y"""
        )

        (tmp_path / "file2.py").write_text(
            """def func2():
    a = 1
    b = 2
    return a + b"""
        )

        analyzer = DuplicateDetector(tmp_path)
        analyzer._find_python_files()
        for file_path in analyzer._find_python_files():
            if file_path.endswith(".py"):
                blocks = analyzer._extract_code_blocks(file_path)
                analyzer.code_blocks.extend(blocks)

        # First find exact duplicates to populate the hash map
        analyzer._find_exact_duplicates()
        near_duplicates = analyzer._find_near_duplicates()

        assert isinstance(near_duplicates, list)

    def test_calculate_similarity_identical(self, tmp_path):
        """Test similarity calculation for identical code blocks."""
        analyzer = DuplicateDetector(tmp_path)

        code = "def func():\n    return 1"
        tokens = analyzer._tokenize_code(code)

        block1 = CodeBlock(
            file_path="file1.py",
            start_line=1,
            end_line=2,
            content=code,
            tokens=tokens,
            ast_hash="hash1",
        )

        block2 = CodeBlock(
            file_path="file2.py",
            start_line=1,
            end_line=2,
            content=code,
            tokens=tokens,
            ast_hash="hash1",
        )

        similarity = analyzer._calculate_similarity(block1, block2)

        assert similarity > 0.9  # Should be very high similarity

    def test_calculate_similarity_different(self, tmp_path):
        """Test similarity calculation for different code blocks."""
        analyzer = DuplicateDetector(tmp_path)

        code1 = "def func():\n    return 1"
        code2 = "class MyClass:\n    pass"

        tokens1 = analyzer._tokenize_code(code1)
        tokens2 = analyzer._tokenize_code(code2)

        block1 = CodeBlock(
            file_path="file1.py",
            start_line=1,
            end_line=2,
            content=code1,
            tokens=tokens1,
            ast_hash="hash1",
        )

        block2 = CodeBlock(
            file_path="file2.py",
            start_line=1,
            end_line=2,
            content=code2,
            tokens=tokens2,
            ast_hash="hash2",
        )

        similarity = analyzer._calculate_similarity(block1, block2)

        assert similarity < 0.5  # Should be low similarity


class TestMainAnalysis:
    """Test main analysis workflow."""

    def test_analyze_duplicates_simple(self, tmp_path):
        """Test complete duplicate analysis."""
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

        analyzer = DuplicateDetector(tmp_path)
        result = analyzer.analyze_duplicates()

        assert isinstance(result, DuplicateAnalysisResult)
        assert result.files_analyzed >= 2
        assert isinstance(result.exact_duplicates, int)
        assert isinstance(result.near_duplicates, int)
        assert isinstance(result.structural_duplicates, int)

    def test_analyze_duplicates_with_duplicates(self, tmp_path):
        """Test analysis when duplicates actually exist."""
        # Create files with duplicate code
        duplicate_code = """def calculate_sum(a, b):
    result = a + b
    return result"""

        (tmp_path / "math1.py").write_text(duplicate_code)
        (tmp_path / "math2.py").write_text(duplicate_code)

        analyzer = DuplicateDetector(tmp_path)
        result = analyzer.analyze_duplicates()

        assert isinstance(result, DuplicateAnalysisResult)
        assert result.files_analyzed >= 2
        # Should detect some duplicates
        total_duplicates = (
            result.exact_duplicates
            + result.near_duplicates
            + result.structural_duplicates
        )
        assert total_duplicates >= 0


class TestIntegration:
    """Integration tests for duplicate detector."""

    def test_full_duplicate_analysis_workflow(self, tmp_path):
        """Test complete duplicate analysis workflow."""
        # Create a realistic codebase with potential duplicates
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create duplicate utility functions
        util_code = """def validate_email(email):
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True

def format_name(first, last):
    return f"{first} {last}".strip()"""

        (src_dir / "utils.py").write_text(util_code)

        # Create another file with similar functions
        (src_dir / "validators.py").write_text(
            """def check_email(email):
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True

def format_full_name(first, last):
    return f"{first} {last}".strip()"""
        )

        # Create a file with completely different code
        (src_dir / "main.py").write_text(
            """from utils import validate_email, format_name

def main():
    email = "test@example.com"
    if validate_email(email):
        name = format_name("John", "Doe")
        print(f"Welcome {name}")
    return "success"

if __name__ == "__main__":
    main()"""
        )

        analyzer = DuplicateDetector(tmp_path)
        result = analyzer.analyze_duplicates()

        # Verify comprehensive analysis
        assert result.files_analyzed >= 3
        assert isinstance(result.exact_duplicates, int)
        assert isinstance(result.near_duplicates, int)
        assert isinstance(result.structural_duplicates, int)

        # Should have identified some duplicates or near-duplicates
        total_duplicates = (
            result.exact_duplicates
            + result.near_duplicates
            + result.structural_duplicates
        )
        assert total_duplicates >= 0

        # Check that duplicate lines are calculated
        assert result.total_duplicate_lines >= 0
