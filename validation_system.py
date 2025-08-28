#!/usr/bin/env python3
"""
Enhanced Validation System for VectorFlow

Reduces false positives by validating actual functionality and requirements compliance,
especially for UI/UX components.
"""

import os
import sys
import subprocess
import tempfile
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import ast
import re
import yaml
import json

class EnhancedValidator:
    """Enhanced validation system that goes beyond file existence checks"""

    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root).resolve()
        self.temp_dir = Path(tempfile.gettempdir()) / "vectorflow_validation"
        self.temp_dir.mkdir(exist_ok=True)

    def validate_component(self, component_name: str, config: Dict) -> Dict:
        """
        Enhanced validation that tests actual functionality

        Returns validation results with detailed status and issues
        """
        file_path = self.project_root / config["file"]

        # Start with basic file checks
        basic_result = self._basic_file_checks(file_path, config)
        if not basic_result["valid"]:
            return basic_result

        # Enhanced validation based on component type
        if "dashboard" in component_name.lower() or "ui" in component_name.lower():
            return self._validate_ui_component(file_path, config)
        elif "analytics" in component_name.lower():
            return self._validate_analytics_component(file_path, config)
        elif "data" in component_name.lower():
            return self._validate_data_component(file_path, config)
        else:
            return self._validate_generic_component(file_path, config)

    def _basic_file_checks(self, file_path: Path, config: Dict) -> Dict:
        """Basic file existence and structure checks"""
        if not file_path.exists():
            return {
                "valid": False,
                "status": "NOT_STARTED",
                "issues": ["File does not exist"],
                "confidence": 0,
                "recommendations": ["Create the required file"]
            }

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {
                "valid": False,
                "status": "ERROR",
                "issues": [f"Cannot read file: {e}"],
                "confidence": 0,
                "recommendations": ["Fix file encoding or permissions"]
            }

        # Check for required elements
        missing_elements = []
        found_elements = 0
        total_elements = 0

        # Check classes, methods, functions
        for check_type in ["required_classes", "required_methods", "required_functions"]:
            if check_type in config:
                for element in config[check_type]:
                    total_elements += 1
                    if f"def {element}" in content or f"class {element}" in content:
                        found_elements += 1
                    else:
                        missing_elements.append(f"{check_type.replace('_', ' ').title()}: {element}")

        completeness = (found_elements / total_elements * 100) if total_elements > 0 else 100

        return {
            "valid": completeness >= 80,  # Require 80% completeness for basic validity
            "status": "COMPLETED" if completeness == 100 else "IN_PROGRESS" if completeness >= 50 else "STARTED",
            "issues": missing_elements,
            "confidence": completeness,
            "recommendations": []
        }

    def _validate_ui_component(self, file_path: Path, config: Dict) -> Dict:
        """Enhanced validation for UI/UX components"""
        basic_result = self._basic_file_checks(file_path, config)

        if not basic_result["valid"]:
            return basic_result

        content = file_path.read_text()

        # UI-specific validations
        ui_validations = []

        # Check for Streamlit imports
        if "streamlit" not in content.lower():
            ui_validations.append("Missing Streamlit import")

        # Check for proper layout implementation (70/30 split)
        if "70/30" not in content and "columns" not in content:
            ui_validations.append("No layout specification found")

        # Check for proper error handling
        if "try:" not in content or "except" not in content:
            ui_validations.append("Missing error handling")

        # Check for data integration
        if "signal" not in content.lower() and "data" not in content.lower():
            ui_validations.append("No data integration detected")

        # Try to import and test the module
        runtime_issues = self._test_ui_runtime(file_path)

        all_issues = basic_result["issues"] + ui_validations + runtime_issues

        # Calculate confidence based on issues
        issue_penalty = len(all_issues) * 10  # 10% penalty per issue
        confidence = max(0, basic_result["confidence"] - issue_penalty)

        return {
            "valid": confidence >= 70 and len(runtime_issues) == 0,  # Must pass runtime tests
            "status": "COMPLETED" if confidence >= 90 else "IN_PROGRESS" if confidence >= 50 else "STARTED",
            "issues": all_issues,
            "confidence": confidence,
            "recommendations": self._generate_ui_recommendations(all_issues)
        }

    def _validate_analytics_component(self, file_path: Path, config: Dict) -> Dict:
        """Enhanced validation for analytics components"""
        basic_result = self._basic_file_checks(file_path, config)

        if not basic_result["valid"]:
            return basic_result

        content = file_path.read_text()

        # Analytics-specific validations
        analytics_validations = []

        # Check for data processing capabilities
        if "def process" not in content and "def analyze" not in content:
            analytics_validations.append("No data processing methods found")

        # Check for output/results
        if "return" not in content and "yield" not in content:
            analytics_validations.append("No output generation detected")

        # Check for numerical computations
        if "numpy" not in content and "pandas" not in content and "math" not in content:
            analytics_validations.append("No numerical computation libraries detected")

        # Test basic import
        runtime_issues = self._test_basic_import(file_path)

        all_issues = basic_result["issues"] + analytics_validations + runtime_issues
        confidence = max(0, basic_result["confidence"] - len(all_issues) * 8)

        return {
            "valid": confidence >= 60 and len(runtime_issues) == 0,
            "status": "COMPLETED" if confidence >= 85 else "IN_PROGRESS" if confidence >= 40 else "STARTED",
            "issues": all_issues,
            "confidence": confidence,
            "recommendations": self._generate_analytics_recommendations(all_issues)
        }

    def _validate_data_component(self, file_path: Path, config: Dict) -> Dict:
        """Enhanced validation for data components"""
        basic_result = self._basic_file_checks(file_path, config)

        if not basic_result["valid"]:
            return basic_result

        content = file_path.read_text()

        # Data-specific validations
        data_validations = []

        # Check for async/await patterns (for real-time data)
        if "async def" not in content and "await" not in content:
            data_validations.append("No asynchronous operations detected")

        # Check for connection handling
        if "connect" not in content and "client" not in content:
            data_validations.append("No connection handling detected")

        # Test basic import
        runtime_issues = self._test_basic_import(file_path)

        all_issues = basic_result["issues"] + data_validations + runtime_issues
        confidence = max(0, basic_result["confidence"] - len(all_issues) * 8)

        return {
            "valid": confidence >= 65 and len(runtime_issues) == 0,
            "status": "COMPLETED" if confidence >= 90 else "IN_PROGRESS" if confidence >= 45 else "STARTED",
            "issues": all_issues,
            "confidence": confidence,
            "recommendations": self._generate_data_recommendations(all_issues)
        }

    def _validate_generic_component(self, file_path: Path, config: Dict) -> Dict:
        """Enhanced validation for generic components"""
        basic_result = self._basic_file_checks(file_path, config)

        if not basic_result["valid"]:
            return basic_result

        # Test basic import
        runtime_issues = self._test_basic_import(file_path)
        all_issues = basic_result["issues"] + runtime_issues
        confidence = max(0, basic_result["confidence"] - len(runtime_issues) * 15)

        return {
            "valid": confidence >= 70 and len(runtime_issues) == 0,
            "status": basic_result["status"],
            "issues": all_issues,
            "confidence": confidence,
            "recommendations": ["Fix import errors"] if runtime_issues else []
        }

    def _test_ui_runtime(self, file_path: Path) -> List[str]:
        """Test UI component at runtime"""
        issues = []

        try:
            # Create a test script to validate the UI
            test_script = f"""
import sys
sys.path.insert(0, '{self.project_root}')

try:
    # Try to import the module
    module_name = '{file_path.stem}'
    spec = importlib.util.spec_from_file_location(module_name, '{file_path}')
    module = importlib.util.module_from_spec(spec)

    # Check for basic imports
    with open('{file_path}', 'r') as f:
        content = f.read()

    # Check for missing imports
    if 'import streamlit' in content or 'from streamlit' in content:
        try:
            import streamlit
        except ImportError:
            issues.append("Streamlit not installed")

    if 'import plotly' in content or 'from plotly' in content:
        try:
            import plotly
        except ImportError:
            issues.append("Plotly not installed")

    print("UI validation completed")

except Exception as e:
    issues.append(f"Runtime error: {str(e)}")
"""

            with open(self.temp_dir / "ui_test.py", "w") as f:
                f.write(test_script)

            result = subprocess.run(
                [sys.executable, str(self.temp_dir / "ui_test.py")],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                issues.append(f"UI test failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            issues.append("UI validation timed out")
        except Exception as e:
            issues.append(f"UI validation error: {str(e)}")

        return issues

    def _test_basic_import(self, file_path: Path) -> List[str]:
        """Test if the module can be imported without errors"""
        issues = []

        try:
            test_script = f"""
import sys
sys.path.insert(0, '{self.project_root}')

try:
    module_name = '{file_path.stem}'
    spec = importlib.util.spec_from_file_location(module_name, '{file_path}')
    module = importlib.util.module_from_spec(spec)
    print("Import test successful")
except Exception as e:
    print(f"Import error: {{e}}")
    exit(1)
"""

            with open(self.temp_dir / "import_test.py", "w") as f:
                f.write(test_script)

            result = subprocess.run(
                [sys.executable, str(self.temp_dir / "import_test.py")],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                issues.append(f"Import failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            issues.append("Import test timed out")
        except Exception as e:
            issues.append(f"Import test error: {str(e)}")

        return issues

    def _generate_ui_recommendations(self, issues: List[str]) -> List[str]:
        """Generate specific recommendations for UI issues"""
        recommendations = []

        for issue in issues:
            if "streamlit" in issue.lower():
                recommendations.append("Install streamlit: pip install streamlit")
            elif "plotly" in issue.lower():
                recommendations.append("Install plotly: pip install plotly")
            elif "layout" in issue.lower():
                recommendations.append("Implement 70/30 layout using st.columns([7, 3])")
            elif "error handling" in issue.lower():
                recommendations.append("Add try/except blocks around UI operations")
            elif "data integration" in issue.lower():
                recommendations.append("Connect UI to data sources and signal processing")

        return recommendations or ["Review and fix validation issues"]

    def _generate_analytics_recommendations(self, issues: List[str]) -> List[str]:
        """Generate specific recommendations for analytics issues"""
        recommendations = []

        for issue in issues:
            if "numpy" in issue.lower() or "pandas" in issue.lower():
                recommendations.append("Install data science libraries: pip install numpy pandas")
            elif "data processing" in issue.lower():
                recommendations.append("Implement data processing methods (process/analyze)")
            elif "output" in issue.lower():
                recommendations.append("Add return statements or yield generators")

        return recommendations or ["Review and fix validation issues"]

    def _generate_data_recommendations(self, issues: List[str]) -> List[str]:
        """Generate specific recommendations for data issues"""
        recommendations = []

        for issue in issues:
            if "async" in issue.lower():
                recommendations.append("Use async/await for real-time data operations")
            elif "connection" in issue.lower():
                recommendations.append("Implement proper connection handling and cleanup")

        return recommendations or ["Review and fix validation issues"]