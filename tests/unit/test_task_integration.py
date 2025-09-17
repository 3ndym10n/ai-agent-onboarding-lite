#!/usr/bin/env python3
"""
Test the Task Integration Logic system.
"""

from ai_onboard.core.task_integration_logic import integrate_task


def test_task_integration():
    """Test various task integration scenarios."""

    print("🧪 Testing Task Integration Logic")
    print("=" * 50)

    # Test Case 1: Critical testing task
    test_task_1 = {
        "name": "Implement Automated Security Testing",
        "description": "Create automated security testing framework to prevent vulnerabilities in production. This is critical for maintaining system integrity.",
        "priority": "critical",
    }

    print("\n📋 Test Case 1: Critical Security Testing Task")
    result_1 = integrate_task(test_task_1)
    print(f"Task Type: {result_1['task_analysis']['task_type']}")
    print(f"Priority: {result_1['task_analysis']['priority_level']}")
    print(
        f"Recommended Phase: {result_1['placement_recommendation']['recommended_phase']}"
    )
    print(f"Placement Type: {result_1['placement_recommendation']['placement_type']}")
    print(".2f")

    # Test Case 2: Documentation task
    test_task_2 = {
        "name": "Create API Documentation",
        "description": "Write comprehensive API documentation with examples and tutorials for developers.",
        "priority": "medium",
    }

    print("\n📋 Test Case 2: Documentation Task")
    result_2 = integrate_task(test_task_2)
    print(f"Task Type: {result_2['task_analysis']['task_type']}")
    print(f"Priority: {result_2['task_analysis']['priority_level']}")
    print(
        f"Recommended Phase: {result_2['placement_recommendation']['recommended_phase']}"
    )
    print(f"Placement Type: {result_2['placement_recommendation']['placement_type']}")
    print(".2f")

    # Test Case 3: Performance optimization
    test_task_3 = {
        "name": "Optimize Database Query Performance",
        "description": "Improve slow database queries that are impacting user experience. Requires database expertise.",
        "priority": "high",
    }

    print("\n📋 Test Case 3: Performance Optimization Task")
    result_3 = integrate_task(test_task_3)
    print(f"Task Type: {result_3['task_analysis']['task_type']}")
    print(f"Priority: {result_3['task_analysis']['priority_level']}")
    print(
        f"Recommended Phase: {result_3['placement_recommendation']['recommended_phase']}"
    )
    print(f"Placement Type: {result_3['placement_recommendation']['placement_type']}")
    print(".2f")
    print(
        f"Skills Required: {', '.join(result_3['task_analysis']['skill_requirements'])}"
    )

    # Test Case 4: Infrastructure task
    test_task_4 = {
        "name": "Set Up CI/CD Pipeline",
        "description": "Implement continuous integration and deployment pipeline for automated testing and deployment.",
        "priority": "high",
    }

    print("\n📋 Test Case 4: Infrastructure CI/CD Task")
    result_4 = integrate_task(test_task_4)
    print(f"Task Type: {result_4['task_analysis']['task_type']}")
    print(f"Priority: {result_4['task_analysis']['priority_level']}")
    print(
        f"Recommended Phase: {result_4['placement_recommendation']['recommended_phase']}"
    )
    print(f"Placement Type: {result_4['placement_recommendation']['placement_type']}")
    print(".2f")

    # Show integration plan for one task
    print("\n📋 Integration Plan for Security Testing Task")
    print("-" * 50)
    plan = result_1["integration_plan"]
    print(f"Task ID: {plan['task_id']}")
    print(f"Estimated Effort: {plan['estimated_effort']}")
    print(f"Required Skills: {', '.join(plan['required_skills'])}")
    print("Integration Steps:")
    for i, step in enumerate(plan["integration_steps"], 1):
        print(f"  {i}. {step}")

    print("\n✅ Task Integration Logic Testing Complete!")


if __name__ == "__main__":
    test_task_integration()
