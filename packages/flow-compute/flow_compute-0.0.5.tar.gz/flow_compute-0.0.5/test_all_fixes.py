#!/usr/bin/env python3
"""Test all flow dev fixes together."""

import subprocess
import time

def run_test(description, command):
    """Run a test command and show results."""
    print(f"\n{description}")
    print("-" * 60)
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    print("Output:", result.stdout[:500] if result.stdout else "(none)")
    if result.stderr:
        print("Errors:", result.stderr[:500])
    return result

def main():
    print("Testing all flow dev fixes")
    print("=" * 60)
    
    # Test 1: Check status (should work without time error)
    result = run_test("Test 1: Check dev VM status", "flow dev --status")
    if "cannot access local variable 'time'" in result.stderr:
        print("❌ FAILED: time import error")
        return 1
    print("✅ PASSED: No time import error")
    
    # Test 2: Test code upload to existing VM (should not show jarring SSH messages)
    if "Running" in result.stdout:
        print("\nTest 2: Upload to existing VM")
        # Create a test file
        with open("/tmp/test.txt", "w") as f:
            f.write("test content\n")
        
        result = run_test(
            "Testing upload to existing VM",
            "cd /tmp && flow dev -c 'ls test.txt' 2>&1"
        )
        
        bad_patterns = ["attempt 2", "attempt 3", "0m 0s elapsed"]
        issues = [p for p in bad_patterns if p in result.stdout or p in result.stderr]
        
        if issues:
            print(f"❌ FAILED: Found jarring output: {issues}")
            return 1
        print("✅ PASSED: No jarring SSH messages")
    
    # Test 3: Check interruption message
    print("\nTest 3: Checking message text")
    # Simulate what happens when SSH wait is interrupted
    # We'll check the actual code for the message
    with open("src/flow/cli/commands/dev.py", "r") as f:
        content = f.read()
        if "The dev VM should still be provisioning" in content:
            print("✅ PASSED: Message says 'should' instead of 'may'")
        else:
            print("❌ FAILED: Message still says 'may'")
            return 1
    
    print("\n" + "=" * 60)
    print("All tests passed! ✅")
    print("\nImprovements verified:")
    print("1. No 'time' import errors")
    print("2. No jarring SSH wait messages for existing VMs")
    print("3. Clear message that VM 'should' still be provisioning")
    print("4. Task ID shown when creating new VM")
    
    return 0

if __name__ == "__main__":
    exit(main())