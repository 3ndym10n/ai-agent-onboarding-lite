#!/usr/bin/env python3
"""
Test script to reproduce and analyze the gate looping issue.
"""

import json
import time as time_module
from pathlib import Path


def test_gate_lifecycle():
    """Test the gate creation, response, and cleanup lifecycle."""

    root = Path.cwd()
    gates_dir = root / ".ai_onboard" / "gates"
    current_gate_file = gates_dir / "current_gate.md"
    response_file = gates_dir / "gate_response.json"

    print("=== Testing Gate Lifecycle ===")

    # Clean up any existing gates
    if current_gate_file.exists():
        current_gate_file.unlink()
        print("✓ Cleaned up existing gate file")
    if response_file.exists():
        response_file.unlink()
        print("✓ Cleaned up existing response file")

    # Also clean up status file
    status_file = gates_dir / "gate_status.json"
    if status_file.exists():
        status_file.unlink()
        print("✓ Cleaned up existing status file")

    # Test 1: Run alignment preview to see decision
    print("\n--- Test 1: Alignment Preview ---")
    from ai_onboard.core import alignment

    preview_result = alignment.preview(root)
    print(f"Confidence: {preview_result['confidence']}")
    print(f"Decision: {preview_result['decision']}")
    print(f"Components: {preview_result['components']}")

    # Test 2: Run IAS gate check (this should create a gate)
    print("\n--- Test 2: IAS Gate Check ---")
    import argparse

    from ai_onboard.cli.commands_core import _ias_gate

    # Create a mock args object for validate command
    args = argparse.Namespace()
    args.cmd = "validate"

    # Debug: Check gate status before calling _ias_gate
    from ai_onboard.core.gate_system import GateSystem

    gate_system = GateSystem(root)
    is_active_before = gate_system.is_gate_active()
    print(f"Gate active before _ias_gate: {is_active_before}")

    gate_result = _ias_gate(args, root)
    print(f"IAS Gate Result: {gate_result}")

    # Check if gate was created
    if current_gate_file.exists():
        print("✓ Gate file created")
        try:
            gate_content = current_gate_file.read_text(encoding="utf-8")
            print(f"Gate content length: {len(gate_content)} chars")
        except UnicodeDecodeError:
            print("✓ Gate file created (encoding issue reading content)")
    else:
        print("✗ No gate file created")

    # Test 3: Create response file manually
    print("\n--- Test 3: Create Response File ---")
    if current_gate_file.exists():
        response_data = {
            "user_responses": [
                "to commit and push the changes to the project",
                "no",
                "to complete the command",
                "step outside the system to do so",
            ],
            "user_decision": "proceed",
            "additional_context": "Test response",
            "timestamp": time_module.time(),
        }

        response_file.write_text(json.dumps(response_data, indent=2), encoding="utf-8")
        print("✓ Response file created")

        # Wait a moment for file system
        time_module.sleep(0.1)

        # Test if response is detected
        if response_file.exists():
            print("✓ Response file exists")
        else:
            print("✗ Response file missing")

    # Test 4: Run IAS gate check again (should now return True)
    print("\n--- Test 4: IAS Gate Check After Response ---")
    gate_result_2 = _ias_gate(args, root)
    print(f"IAS Gate Result after response: {gate_result_2}")

    # Test 5: Check if gate files are cleaned up
    print("\n--- Test 5: Gate Cleanup Check ---")
    if current_gate_file.exists():
        print("✗ Gate file still exists (should be cleaned up)")
    else:
        print("✓ Gate file cleaned up")

    if response_file.exists():
        print("✗ Response file still exists (should be cleaned up)")
    else:
        print("✓ Response file cleaned up")

    # Test 6: Wait and try again (simulate timeout cleanup)
    print("\n--- Test 6: Timeout Cleanup Simulation ---")
    print("Waiting 11 seconds to simulate timeout...")
    time_module.sleep(11)

    # Debug: Check gate status after wait
    is_active_after_wait = gate_system.is_gate_active()
    print(f"Gate active after 11 second wait: {is_active_after_wait}")

    # Try IAS gate check again
    gate_result_3 = _ias_gate(args, root)
    print(f"IAS Gate Result after timeout: {gate_result_3}")

    # Final cleanup check
    print("\n--- Final Cleanup Check ---")
    if current_gate_file.exists():
        print("✗ Gate file still exists")
    else:
        print("✓ Gate file cleaned up")

    if response_file.exists():
        print("✗ Response file still exists")
    else:
        print("✓ Response file cleaned up")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_gate_lifecycle()
