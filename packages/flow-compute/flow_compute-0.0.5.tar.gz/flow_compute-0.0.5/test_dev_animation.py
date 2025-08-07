#!/usr/bin/env python3
"""Test script to check if flow dev shows the animation."""

import subprocess
import threading
import time
import sys

def run_flow_dev():
    """Run flow dev and capture output."""
    proc = subprocess.Popen(
        ["flow", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Collect output for a few seconds
    output_lines = []
    start_time = time.time()
    
    def read_output():
        for line in iter(proc.stdout.readline, ''):
            if line:
                output_lines.append(line.rstrip())
                print(f"STDOUT: {line.rstrip()}")
                
    def read_error():
        for line in iter(proc.stderr.readline, ''):
            if line:
                output_lines.append(f"STDERR: {line.rstrip()}")
                print(f"STDERR: {line.rstrip()}")
    
    # Start threads to read output
    stdout_thread = threading.Thread(target=read_output, daemon=True)
    stderr_thread = threading.Thread(target=read_error, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait a few seconds to see what happens
    time.sleep(5)
    
    # Kill the process
    proc.terminate()
    time.sleep(0.5)
    if proc.poll() is None:
        proc.kill()
    
    # Wait for threads to finish
    stdout_thread.join(timeout=1)
    stderr_thread.join(timeout=1)
    
    return output_lines

if __name__ == "__main__":
    print("Testing flow dev animation...")
    print("=" * 60)
    
    lines = run_flow_dev()
    
    print("\n" + "=" * 60)
    print("Captured output:")
    for line in lines[:20]:  # Show first 20 lines
        print(line)
    
    # Check for animation
    has_animation = any("Connecting to dev VM" in line for line in lines)
    has_using_msg = any("Using existing dev VM" in line for line in lines)
    
    print("\n" + "=" * 60)
    if has_using_msg:
        print("✓ Found 'Using existing dev VM' message")
    else:
        print("✗ Missing 'Using existing dev VM' message")
        
    if has_animation:
        print("✓ Found 'Connecting to dev VM' animation")
    else:
        print("✗ Missing 'Connecting to dev VM' animation")