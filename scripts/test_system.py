#!/usr/bin/env python3
"""
System test script for ai-onboard.
Tests all major system capabilities and reports status.
"""

import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_onboard.core.alignment import preview
from ai_onboard.core.universal_error_monitor import get_error_monitor
from ai_onboard.core.vision_interrogator import get_vision_interrogator


def test_error_monitoring():
    """Test the error monitoring system."""
    print("🔍 Testing error monitoring system...")

    monitor = get_error_monitor(Path.cwd())

    # Test error interception
    try:
        with monitor.monitor_command_execution(
            "test_command", "test_agent", "test_session"
        ):
            raise ValueError("Test error for system validation")
    except ValueError:
        pass  # Expected

    # Test capability tracking
    monitor.track_capability_usage(
        "system_test", {"test": "error_monitoring", "success": True}
    )

    # Get usage report
    report = monitor.get_usage_report()

    print("✅ Error monitoring active")
    print(f"   - Total capability uses: {report['total_capability_uses']}")
    print(f"   - Error rate: {report['error_rate']:.2%}")
    print(f"   - Recent errors: {len(report['recent_errors'])}")

    return True


def test_vision_system():
    """Test the vision interrogation system."""
    print("🔍 Testing vision interrogation system...")

    interrogator = get_vision_interrogator(Path.cwd())
    readiness = interrogator.check_vision_readiness()

    print("✅ Vision system status:")
    print(f"   - Ready for agents: {readiness['ready_for_agents']}")
    print(f"   - Interrogation complete: {readiness['interrogation_complete']}")
    print(f"   - Vision clarity: {readiness['vision_clarity']['score']:.2f}")

    return readiness["ready_for_agents"]


def test_alignment_system():
    """Test the alignment system."""
    print("🔍 Testing alignment system...")

    alignment_data = preview(Path.cwd())

    print("✅ Alignment system status:")
    print(f"   - Confidence: {alignment_data['confidence']:.2f}")
    print(f"   - Decision: {alignment_data['decision']}")
    print(
        f"   - Vision completeness: {alignment_data['components']['vision_completeness']:.2f}"
    )

    return alignment_data["confidence"] > 0.7


def test_project_plan():
    """Test the project planning system."""
    print("🔍 Testing project planning system...")

    plan_path = Path.cwd() / ".ai_onboard" / "plan.json"
    if not plan_path.exists():
        print("❌ No project plan found")
        return False

    with open(plan_path, "r") as f:
        plan = json.load(f)

    print("✅ Project plan status:")
    print(f"   - Total tasks: {len(plan.get('tasks', []))}")
    print(
        f"   - Total effort: {sum(t.get('effort_days', 0) for t in plan.get('tasks', []))} days"
    )
    print(f"   - Critical path: {len(plan.get('critical_path', []))} tasks")

    return len(plan.get("tasks", [])) > 0


def main():
    """Run all system tests."""
    print("🧪 Running ai-onboard system tests...\n")

    tests = [
        ("Error Monitoring", test_error_monitoring),
        ("Vision System", test_vision_system),
        ("Alignment System", test_alignment_system),
        ("Project Planning", test_project_plan),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
        print()

    # Summary
    print("📊 Test Results Summary:")
    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All systems operational!")
        return 0
    else:
        print("⚠️  Some systems need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
