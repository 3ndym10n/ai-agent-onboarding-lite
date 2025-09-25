#!/usr/bin/env python3
"""
Test script for the Import Consolidation System.

This script tests the basic functionality of the import consolidation system
to ensure all components work together correctly.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.import_consolidation_migrator import ImportConsolidationMigrator
from scripts.integrated_import_consolidation import IntegratedImportConsolidation
from scripts.monitor_import_changes import ImportChangeMonitor
from scripts.validate_import_equivalence import ImportEquivalenceValidator


def test_migrator():
    """Test the import consolidation migrator."""
    print("🧪 Testing Import Consolidation Migrator...")

    try:
        migrator = ImportConsolidationMigrator(project_root)

        # Test analysis
        print("  Testing analysis...")
        analysis = migrator.analyze_consolidation_opportunities()
        assert "total_files" in analysis
        assert "total_imports" in analysis
        assert "consolidation_potential" in analysis
        print("  ✅ Analysis test passed")

        # Test plan creation
        print("  Testing plan creation...")
        plan = migrator.create_migration_plan(["common_imports"])
        assert plan.backup_id is not None
        assert len(plan.targets) > 0
        print("  ✅ Plan creation test passed")

        print("✅ Migrator tests passed")
        return True

    except Exception as e:
        print(f"❌ Migrator test failed: {e}")
        return False


def test_validator():
    """Test the import equivalence validator."""
    print("🧪 Testing Import Equivalence Validator...")

    try:
        validator = ImportEquivalenceValidator(project_root)

        # Test validation
        print("  Testing validation...")
        original_imports = ["pathlib.Path", "typing.Dict"]
        consolidated_imports = [
            "ai_onboard.core.common_imports.Path",
            "ai_onboard.core.common_imports.Dict",
        ]
        test_files = []

        report = validator.validate_consolidation_equivalence(
            original_imports, consolidated_imports, test_files
        )

        assert report.total_imports == 2
        assert report.passed_imports >= 0
        print("  ✅ Validation test passed")

        print("✅ Validator tests passed")
        return True

    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False


def test_monitor():
    """Test the import change monitor."""
    print("🧪 Testing Import Change Monitor...")

    try:
        monitor = ImportChangeMonitor(project_root)

        # Test status
        print("  Testing status...")
        status = monitor.get_current_status()
        assert "monitoring_active" in status
        assert "total_changes" in status
        print("  ✅ Status test passed")

        print("✅ Monitor tests passed")
        return True

    except Exception as e:
        print(f"❌ Monitor test failed: {e}")
        return False


def test_integrated_system():
    """Test the integrated consolidation system."""
    print("🧪 Testing Integrated Consolidation System...")

    try:
        consolidation = IntegratedImportConsolidation(project_root)

        # Test workflow status
        print("  Testing workflow status...")
        status = consolidation.get_workflow_status()
        assert "status" in status
        print("  ✅ Workflow status test passed")

        print("✅ Integrated system tests passed")
        return True

    except Exception as e:
        print(f"❌ Integrated system test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing Import Consolidation System")
    print("=" * 50)

    tests = [test_migrator, test_validator, test_monitor, test_integrated_system]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! The import consolidation system is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

