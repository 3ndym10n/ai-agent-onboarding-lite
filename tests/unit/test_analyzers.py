#!/usr/bin/env python3
"""
Consolidated Analyzer Tests

This module consolidates all analyzer-related tests into a single,
parameterized test suite for better maintainability and reduced duplication.
"""

import tempfile
from pathlib import Path

import pytest

from ai_onboard.core.ai_integration.code_quality_analyzer import CodeQualityAnalyzer
from ai_onboard.core.ai_integration.duplicate_detector import DuplicateDetector
from ai_onboard.core.ai_integration.file_organization_analyzer import (
    FileOrganizationAnalyzer,
)
from ai_onboard.core.ai_integration.performance_trend_analyzer import (
    PerformanceTrendAnalyzer,
)


class TestAnalyzers:
    """Consolidated test suite for all analyzer components."""

    @pytest.fixture
    def temp_root(self):
        """Provide temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.mark.parametrize(
        "analyzer_type,analyzer_class,expected_attrs",
        [
            (
                "code_quality",
                CodeQualityAnalyzer,
                ["analyze_code_quality", "get_quality_score"],
            ),
            (
                "file_organization",
                FileOrganizationAnalyzer,
                ["analyze_organization", "get_organization_score"],
            ),
            (
                "duplicate",
                DuplicateDetector,
                ["detect_duplicates", "get_duplicate_score"],
            ),
            (
                "performance_trend",
                PerformanceTrendAnalyzer,
                ["analyze_trends", "get_performance_score"],
            ),
        ],
    )
    def test_analyzer_initialization(
        self, analyzer_type, analyzer_class, expected_attrs, temp_root
    ):
        """Test that all analyzers initialize correctly."""
        analyzer = analyzer_class(temp_root)

        assert analyzer is not None
        for attr in expected_attrs:
            assert hasattr(analyzer, attr)

        print(f"✅ {analyzer_type} analyzer initialized successfully")

    def test_code_quality_analyzer(self, temp_root):
        """Test code quality analyzer functionality."""
        analyzer = CodeQualityAnalyzer(temp_root)

        # Test with sample code
        sample_code = """
def test_function():
    x = 1
    y = 2
    return x + y
"""

        result = analyzer.analyze_code_quality(sample_code)
        assert result is not None
        assert "quality_score" in result
        assert "issues" in result

        print(f"✅ Code quality analysis: {result['quality_score']:.2f} score")

    def test_file_organization_analyzer(self, temp_root):
        """Test file organization analyzer functionality."""
        analyzer = FileOrganizationAnalyzer(temp_root)

        # Create test file structure
        test_file = temp_root / "test_module.py"
        test_file.write_text("def test_function(): pass")

        result = analyzer.analyze_organization()
        assert result is not None
        assert "organization_score" in result

        print(
            f"✅ File organization analysis: {result['organization_score']:.2f} score"
        )

    def test_duplicate_detector(self, temp_root):
        """Test duplicate detector functionality."""
        detector = DuplicateDetector(temp_root)

        # Add duplicate code blocks
        detector.add_code_block("block1", "def func(): return 1")
        detector.add_code_block("block2", "def func(): return 1")  # Duplicate

        result = detector.detect_duplicates()
        assert result is not None
        assert "duplicates" in result

        print(f"✅ Duplicate detection: Found {len(result['duplicates'])} duplicates")

    def test_performance_trend_analyzer(self, temp_root):
        """Test performance trend analyzer functionality."""
        analyzer = PerformanceTrendAnalyzer(temp_root)

        # Add performance metrics
        analyzer.add_performance_metric("test_operation", 0.5, {"memory": 100})
        analyzer.add_performance_metric("test_operation", 0.3, {"memory": 120})

        trends = analyzer.analyze_trends()
        assert trends is not None
        assert "trend_direction" in trends

        print(f"✅ Performance trend analysis: {trends['trend_direction']}")

    def test_analyzer_integration(self, temp_root):
        """Test that analyzers work together."""
        # Test basic integration without complex dependencies
        code_analyzer = CodeQualityAnalyzer(temp_root)
        org_analyzer = FileOrganizationAnalyzer(temp_root)

        # Both should initialize without errors
        assert code_analyzer is not None
        assert org_analyzer is not None

        print("✅ Analyzer integration: Components work independently")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
