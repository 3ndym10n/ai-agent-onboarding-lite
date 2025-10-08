#!/usr/bin/env python3
"""
Analyze linter errors to categorize and estimate fix effort.
"""
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def run_mypy():
    """Run mypy and capture errors."""
    try:
        result = subprocess.run(
            ["python", "-m", "mypy", "."], capture_output=True, text=True, timeout=60
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Mypy timed out"
    except FileNotFoundError:
        return "Mypy not found"


def run_flake8():
    """Run flake8 and capture errors."""
    try:
        result = subprocess.run(
            ["python", "-m", "flake8", "--format=json", "."],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Flake8 timed out"
    except FileNotFoundError:
        return "Flake8 not found"


def analyze_error_patterns():
    """Analyze patterns in linter errors."""
    print("Analyzing linter errors...")

    # Run linters
    mypy_output = run_mypy()
    flake8_output = run_flake8()

    if mypy_output == "Mypy not found" and flake8_output == "Flake8 not found":
        print("No linters available")
        return

    # Analyze mypy errors
    error_patterns = defaultdict(int)
    file_count = 0
    total_errors = 0

    if mypy_output != "Mypy not found" and mypy_output != "Mypy timed out":
        lines = mypy_output.split("\n")
        for line in lines:
            if ":" in line and ".py" in line:
                file_count += 1
                total_errors += 1

                # Categorize error types
                if "Import" in line and "could not be resolved" in line:
                    error_patterns["import_resolution"] += 1
                elif "Skipping analyzing" in line:
                    error_patterns["missing_stubs"] += 1
                elif "Incompatible types" in line:
                    error_patterns["type_incompatible"] += 1
                elif "Returning" in line and "Any" in line:
                    error_patterns["return_any"] += 1
                elif "Need type annotation" in line:
                    error_patterns["missing_annotation"] += 1
                elif "not defined" in line:
                    error_patterns["undefined_name"] += 1
                elif "blank line" in line:
                    error_patterns["formatting"] += 1
                elif "line too long" in line:
                    error_patterns["line_length"] += 1
                elif "not subscriptable" in line:
                    error_patterns["typing_issues"] += 1
                else:
                    error_patterns["other"] += 1

    print("LINTER ERROR ANALYSIS")
    print("=" * 50)
    print(f"Total files with errors: {file_count}")
    print(f"Estimated total errors: {total_errors}")
    print()

    print("ERROR CATEGORIES")
    print("-" * 30)
    for category, count in sorted(
        error_patterns.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"{category.replace('_', ' ').title()}: {count}")
    print()

    # Estimate effort
    effort_estimate = estimate_fix_effort(error_patterns)

    print("EFFORT ESTIMATE")
    print("-" * 30)
    for category, effort in effort_estimate.items():
        print(f"{category}: {effort}")

    return error_patterns


def estimate_fix_effort(error_patterns):
    """Estimate time to fix different categories of errors."""
    estimates = {}

    # Effort estimates in minutes per error
    effort_per_error = {
        "import_resolution": 5,  # Usually simple import fixes
        "missing_stubs": 2,  # Add type: ignore or install stubs
        "type_incompatible": 8,  # May need significant type fixes
        "return_any": 3,  # Usually simple type annotations
        "missing_annotation": 2,  # Add type hints
        "undefined_name": 5,  # Fix imports or variable definitions
        "formatting": 1,  # Auto-fixable with tools
        "line_length": 2,  # Usually simple line breaks
        "typing_issues": 5,  # Generic typing problems
        "other": 10,  # Unknown complexity
    }

    for category, count in error_patterns.items():
        if count > 0:
            time_per_error = effort_per_error.get(category, 10)
            total_time = count * time_per_error
            hours = total_time // 60
            minutes = total_time % 60

            if hours > 0:
                estimates[category.replace("_", " ").title()] = f"{hours}h {minutes}m"
            else:
                estimates[category.replace("_", " ").title()] = f"{minutes}m"

    return estimates


if __name__ == "__main__":
    analyze_error_patterns()
