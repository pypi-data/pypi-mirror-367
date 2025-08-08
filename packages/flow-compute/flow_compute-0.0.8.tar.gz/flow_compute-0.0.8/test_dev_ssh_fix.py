#!/usr/bin/env python3
"""Test script to verify the SSH waiting fix for flow dev."""

import subprocess
import sys
import time

def run_command(cmd):
    """Run a command and capture output."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=True, 
        text=True
    )
    return result

def test_dev_ssh_output():
    """Test that flow dev doesn't show jarring SSH wait messages."""
    
    print("Testing flow dev SSH output fix...")
    print("=" * 60)
    
    # First, check if there's an existing dev VM
    result = run_command("flow dev --status")
    
    if "No dev VM running" in result.stdout:
        print("No existing dev VM found. Starting one...")
        # Start a dev VM
        result = run_command("flow dev -c 'echo test' --no-upload")
        print("Output:", result.stdout)
        print("Errors:", result.stderr)
        
        # Wait a bit for VM to be ready
        time.sleep(5)
    
    # Now test the upload to an existing VM
    print("\nTesting upload to existing dev VM...")
    print("-" * 60)
    
    # Create a small test file to upload
    with open("/tmp/test_upload.txt", "w") as f:
        f.write("Test file for SSH fix verification\n")
    
    # Run flow dev with upload to existing VM
    result = run_command("cd /tmp && flow dev -c 'ls -la test_upload.txt' 2>&1")
    
    print("Full output:")
    print(result.stdout)
    
    # Check for the jarring output patterns
    bad_patterns = [
        "Waiting for SSH access (0m 0s elapsed)",
        "attempt 2",
        "attempt 3",
        "attempt 4",
    ]
    
    issues_found = []
    for pattern in bad_patterns:
        if pattern in result.stdout or pattern in result.stderr:
            issues_found.append(pattern)
    
    print("\n" + "=" * 60)
    if issues_found:
        print("❌ FAILED: Jarring output still present:")
        for issue in issues_found:
            print(f"  - Found: '{issue}'")
        return 1
    else:
        print("✅ SUCCESS: No jarring SSH wait messages found!")
        print("The output is clean and professional.")
        return 0

if __name__ == "__main__":
    sys.exit(test_dev_ssh_output())