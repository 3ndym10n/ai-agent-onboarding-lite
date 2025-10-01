"""
Tests for vision planning system.

This module tests the core planning functionality that generates
project plans from charter data, including WBS, tasks, dependencies,
and risk analysis.
"""

from unittest.mock import patch

import pytest

from ai_onboard.core.vision.planning import (
    _analyze_dependencies,
    _generate_charter_aware_milestones,
    _generate_charter_aware_risks,
    _generate_charter_aware_wbs,
    _generate_detailed_tasks,
    build,
)


class TestPlanningBuild:
    """Test the main build function."""

    @patch("ai_onboard.core.vision.planning.utils.write_json")
    @patch("ai_onboard.core.vision.planning.utils.read_json")
    def test_build_successful(self, mock_read_json, mock_write_json, tmp_path):
        """Test successful plan building."""
        # Mock charter data
        charter_data = {
            "project_name": "Test Project",
            "preferred_methodology": "agile",
            "scope": ["feature1", "feature2"],
            "technologies": ["python", "django"],
            "complexity": "medium",
        }
        mock_read_json.return_value = charter_data

        # Execute
        result = build(tmp_path)

        # Verify charter was read
        mock_read_json.assert_called_once()

        # Verify plan was written
        mock_write_json.assert_called_once()

        # Verify return value structure
        assert isinstance(result, dict)
        assert "methodology" in result
        assert "wbs" in result
        assert "tasks" in result
        assert "milestones" in result
        assert "risks" in result

    @patch("ai_onboard.core.vision.planning.utils.read_json")
    def test_build_missing_charter(self, mock_read_json, tmp_path):
        """Test build fails when charter is missing."""
        mock_read_json.return_value = None

        with pytest.raises(SystemExit, match="Missing charter"):
            build(tmp_path)


class TestWBSGeneration:
    """Test Work Breakdown Structure generation."""

    def test_generate_wbs_basic(self):
        """Test basic WBS generation."""
        charter = {
            "scope": ["authentication", "user_management", "api"],
            "technologies": ["python", "django"],
            "complexity": "medium",
        }

        wbs = _generate_charter_aware_wbs(charter)

        assert isinstance(wbs, list)
        assert len(wbs) > 0

        # Check WBS structure
        for item in wbs:
            assert "id" in item
            assert "name" in item
            assert "deps" in item

    def test_generate_wbs_empty_scope(self):
        """Test WBS generation with empty scope."""
        charter = {
            "scope": [],
            "technologies": ["python"],
            "complexity": "low",
        }

        wbs = _generate_charter_aware_wbs(charter)

        assert isinstance(wbs, list)


class TestMilestoneGeneration:
    """Test milestone generation."""

    def test_generate_milestones(self):
        """Test milestone generation from charter."""
        charter = {
            "timeline": "3 months",
            "methodology": "agile",
            "scope": ["feature1", "feature2"],
        }

        milestones = _generate_charter_aware_milestones(charter)

        assert isinstance(milestones, list)
        assert len(milestones) > 0

        # Check milestone structure
        for milestone in milestones:
            assert "name" in milestone
            assert "description" in milestone

    def test_generate_milestones_empty(self):
        """Test milestone generation with minimal charter."""
        charter = {}

        milestones = _generate_charter_aware_milestones(charter)

        assert isinstance(milestones, list)


class TestRiskGeneration:
    """Test risk assessment generation."""

    def test_generate_risks(self):
        """Test risk generation based on charter."""
        charter = {
            "technologies": ["python", "react", "kubernetes"],
            "complexity": "high",
            "team_size": 3,
            "timeline": "2 months",
        }

        risks = _generate_charter_aware_risks(charter)

        assert isinstance(risks, list)
        # May return empty list depending on logic
        if len(risks) > 0:
            # Check risk structure
            for risk in risks:
                assert "id" in risk
                assert "description" in risk
                assert "probability" in risk
                assert "impact" in risk

    def test_generate_risks_minimal(self):
        """Test risk generation with minimal data."""
        charter = {"technologies": ["python"]}

        risks = _generate_charter_aware_risks(charter)

        assert isinstance(risks, list)


class TestTaskGeneration:
    """Test detailed task generation."""

    def test_generate_tasks(self):
        """Test task generation from charter and WBS."""
        charter = {
            "technologies": ["python", "django"],
            "methodology": "agile",
        }
        wbs = [
            {"id": "1", "name": "Setup", "deps": []},
            {"id": "2", "name": "Development", "deps": ["1"]},
        ]

        tasks = _generate_detailed_tasks(charter, wbs)

        assert isinstance(tasks, list)
        # May return empty list depending on logic
        if len(tasks) > 0:
            # Check task structure
            for task in tasks:
                assert "id" in task
                assert "name" in task
                assert "description" in task

    def test_generate_tasks_empty_wbs(self):
        """Test task generation with empty WBS."""
        charter = {"technologies": ["python"]}
        wbs = []

        tasks = _generate_detailed_tasks(charter, wbs)

        assert isinstance(tasks, list)


class TestDependencyAnalysis:
    """Test dependency analysis functionality."""

    def test_analyze_dependencies(self):
        """Test dependency analysis for tasks."""
        tasks = [
            {
                "id": "task1",
                "name": "Setup",
                "type": "setup",
                "wbs_id": "C1",
                "effort_days": 2,
                "dependencies": [],
            },
            {
                "id": "task2",
                "name": "Develop",
                "type": "development",
                "wbs_id": "C2",
                "effort_days": 5,
                "dependencies": ["task1"],
            },
            {
                "id": "task3",
                "name": "Test",
                "type": "testing",
                "wbs_id": "C3",
                "effort_days": 3,
                "dependencies": ["task2"],
            },
        ]

        analysis = _analyze_dependencies(tasks)

        assert isinstance(analysis, dict)
        assert "dependencies" in analysis
        assert "critical_path" in analysis
        assert "parallel_work" in analysis

    def test_analyze_dependencies_empty(self):
        """Test dependency analysis with no tasks."""
        tasks = []

        analysis = _analyze_dependencies(tasks)

        assert isinstance(analysis, dict)
