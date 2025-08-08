#!/usr/bin/env python3
"""Test script to verify the time import fix."""

import subprocess
import sys

def test_flow_dev():
    """Test that flow dev runs without import errors."""
    
    print("Testing flow dev time import fix...")
    print("=" * 60)
    
    # Test flow dev status (should work without errors)
    result = subprocess.run(
        ["flow", "dev", "--status"],
        capture_output=True,
        text=True
    )
    
    print("Command: flow dev --status")
    print("Return code:", result.returncode)
    print("Output:", result.stdout)
    
    if "cannot access local variable 'time'" in result.stderr:
        print("❌ FAILED: time import error still present")
        print("Error:", result.stderr)
        return 1
    
    if result.returncode != 0 and "No dev VM running" not in result.stdout:
        print("❌ FAILED: Command failed with unexpected error")
        print("Error:", result.stderr)
        return 1
    
    print("✅ SUCCESS: No time import errors!")
    return 0

if __name__ == "__main__":
    sys.exit(test_flow_dev())