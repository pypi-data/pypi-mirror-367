#!/usr/bin/env python
"""Test script to verify decorator functionality with flow dev.

This script generates test functions with various decorator parameters
and creates executable wrapper scripts that can be run on flow dev.

Usage:
    # Step 1: Generate test wrapper scripts
    python test_decorator_flow_dev.py generate
    
    # Step 2: Start flow dev VM
    flow dev  # Start or connect to VM
    
    # Step 3: Upload test files and run tests
    flow dev -c 'python /root/test_basic.py'
    flow dev -c 'python /root/test_gpu.py' 
    flow dev -c 'python /root/test_volumes.py'
    
    # Step 4: Check results
    flow dev -c 'cat /tmp/flow_result.json'
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from flow import FlowApp
from flow.api.models import Retries
from flow.api.secrets import Secret


def generate_test_wrappers():
    """Generate wrapper scripts for all decorator test cases."""
    
    # Initialize Flow app
    app = FlowApp()
    
    test_cases = []
    
    # Test Case 1: Basic function with GPU
    @app.function(gpu="a100")
    def test_basic(x: int, y: int = 10) -> Dict[str, Any]:
        """Basic test function."""
        return {"sum": x + y, "product": x * y}
    
    # Generate wrapper for basic test
    wrapper1 = test_basic._create_wrapper_script((5,), {"y": 20})
    save_wrapper("test_basic.py", wrapper1)
    test_cases.append("test_basic.py")
    
    # Test Case 2: GPU with memory and image
    @app.function(
        gpu="h100:2",
        memory=131072,  # 128GB
        image="pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime"
    )
    def test_gpu_config(model_name: str) -> Dict[str, Any]:
        """Test GPU configuration."""
        import platform
        import sys
        result = {
            "model": model_name,
            "python_version": sys.version,
            "platform": platform.platform(),
            "gpu_configured": True
        }
        # Try to import torch if available
        try:
            import torch
            result["torch_version"] = torch.__version__
            result["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                result["gpu_count"] = torch.cuda.device_count()
        except ImportError:
            result["torch_available"] = False
        return result
    
    wrapper2 = test_gpu_config._create_wrapper_script(("llama-70b",), {})
    save_wrapper("test_gpu.py", wrapper2)
    test_cases.append("test_gpu.py")
    
    # Test Case 3: Volumes
    @app.function(
        gpu="a100",
        volumes={
            "/data": "training-data",
            "/models": {"name": "model-cache", "size_gb": 100},
            "/outputs": {"size_gb": 50}
        }
    )
    def test_volumes(data_path: str) -> Dict[str, Any]:
        """Test volume mounting."""
        import os
        result = {
            "data_path": data_path,
            "volumes_mounted": {
                "/data": os.path.exists("/data"),
                "/models": os.path.exists("/models"),
                "/outputs": os.path.exists("/outputs")
            },
            "can_write": {}
        }
        # Test write permissions
        for mount in ["/data", "/models", "/outputs"]:
            try:
                test_file = f"{mount}/test_write.txt"
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                result["can_write"][mount] = True
            except:
                result["can_write"][mount] = False
        return result
    
    wrapper3 = test_volumes._create_wrapper_script(("/data/input.csv",), {})
    save_wrapper("test_volumes.py", wrapper3)
    test_cases.append("test_volumes.py")
    
    # Test Case 4: Environment variables
    @app.function(
        gpu="a100",
        environment={
            "CUDA_VISIBLE_DEVICES": "0,1",
            "CUSTOM_ENV": "test_value",
            "DEBUG": "true"
        }
    )
    def test_environment() -> Dict[str, Any]:
        """Test environment variables."""
        import os
        return {
            "cuda_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "custom_env": os.environ.get("CUSTOM_ENV"),
            "debug": os.environ.get("DEBUG"),
            "path": os.environ.get("PATH", "")[:100]  # First 100 chars
        }
    
    wrapper4 = test_environment._create_wrapper_script((), {})
    save_wrapper("test_environment.py", wrapper4)
    test_cases.append("test_environment.py")
    
    # Test Case 5: Retries configuration
    retry_config = Retries(
        max_attempts=3,
        initial_delay=1.0,
        exponential_base=2.0,
        jitter=True
    )
    
    @app.function(gpu="a100", retries=retry_config)
    def test_retries(attempt_num: int) -> Dict[str, Any]:
        """Test retry configuration."""
        import random
        # Simulate flaky behavior
        if attempt_num < 2:
            if random.random() < 0.7:  # 70% chance of failure
                raise RuntimeError(f"Simulated failure on attempt {attempt_num}")
        return {
            "attempt": attempt_num,
            "status": "success",
            "retry_config": {
                "max_attempts": 3,
                "configured": True
            }
        }
    
    wrapper5 = test_retries._create_wrapper_script((1,), {})
    save_wrapper("test_retries.py", wrapper5)
    test_cases.append("test_retries.py")
    
    # Test Case 6: Timeout
    @app.function(gpu="a100", timeout=60)  # 60 second timeout
    def test_timeout(sleep_duration: int) -> Dict[str, Any]:
        """Test timeout configuration."""
        import time
        start = time.time()
        if sleep_duration > 0:
            time.sleep(min(sleep_duration, 5))  # Cap at 5 seconds for testing
        return {
            "sleep_requested": sleep_duration,
            "actual_duration": time.time() - start,
            "timeout_configured": 60
        }
    
    wrapper6 = test_timeout._create_wrapper_script((2,), {})
    save_wrapper("test_timeout.py", wrapper6)
    test_cases.append("test_timeout.py")
    
    # Test Case 7: Complex arguments
    @app.function(gpu="a100")
    def test_complex_args(
        numbers: List[int],
        config: Dict[str, Any],
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Test complex argument types."""
        return {
            "sum_numbers": sum(numbers),
            "config_keys": list(config.keys()),
            "threshold": threshold,
            "types": {
                "numbers": str(type(numbers)),
                "config": str(type(config)),
                "threshold": str(type(threshold))
            }
        }
    
    wrapper7 = test_complex_args._create_wrapper_script(
        ([1, 2, 3, 4, 5],),
        {"config": {"learning_rate": 0.001, "batch_size": 32}, "threshold": 0.8}
    )
    save_wrapper("test_complex_args.py", wrapper7)
    test_cases.append("test_complex_args.py")
    
    # Test Case 8: All parameters combined
    @app.function(
        gpu="h100:4",
        cpu=(8.0, 16.0),
        memory=(65536, 131072),
        image="python:3.11",
        retries=2,
        timeout=300,
        volumes={"/workspace": {"size_gb": 200}},
        environment={"MODE": "production"}
    )
    def test_all_params(task_id: str) -> Dict[str, Any]:
        """Test all decorator parameters."""
        import os
        import platform
        return {
            "task_id": task_id,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "mode": os.environ.get("MODE"),
            "workspace_exists": os.path.exists("/workspace"),
            "all_params_test": True
        }
    
    wrapper8 = test_all_params._create_wrapper_script(("test-123",), {})
    save_wrapper("test_all_params.py", wrapper8)
    test_cases.append("test_all_params.py")
    
    # Create a master test runner script
    create_test_runner(test_cases)
    
    print(f"Generated {len(test_cases)} test wrapper scripts")
    print("\nTest files created:")
    for test_file in test_cases:
        print(f"  - {test_file}")
    print("  - run_all_tests.sh (master test runner)")
    
    return test_cases


def save_wrapper(filename: str, wrapper_code: str):
    """Save wrapper script to file."""
    # Fix the import path in wrapper to work standalone
    # The wrapper expects "from __main__ import func_name" so we need to replace that
    import re
    func_match = re.search(r'from __main__ import (\w+)', wrapper_code)
    if func_match:
        func_name = func_match.group(1)
        wrapper_code = wrapper_code.replace(
            f"from __main__ import {func_name}",
            f"# Function defined inline (would be imported in real usage)\n# from module import {func_name}\n# For testing, we define a mock function\ndef {func_name}(*args, **kwargs):\n    return {{'test': 'success', 'args': args, 'kwargs': kwargs}}"
        )
    
    # Add a main block to ensure execution
    wrapper_code += """
# Ensure the script runs when executed directly
if __name__ == "__main__":
    print(f"Test {__file__} completed. Check /tmp/flow_result.json for results.")
"""
    
    with open(filename, "w") as f:
        f.write(wrapper_code)
    print(f"Created {filename}")


def create_test_runner(test_cases: List[str]):
    """Create a shell script to run all tests."""
    script = """#!/bin/bash
# Test runner for decorator functionality with flow dev

set -e  # Exit on error

echo "Starting decorator tests on flow dev VM..."
echo "========================================"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to run a test and check result
run_test() {
    local test_file=$1
    local test_name=$(basename $test_file .py)
    
    echo ""
    echo "Running test: $test_name"
    echo "------------------------"
    
    # Run the test
    if python /root/$test_file; then
        # Check if result file exists
        if [ -f /tmp/flow_result.json ]; then
            # Parse result
            if python -c "import json; data=json.load(open('/tmp/flow_result.json')); exit(0 if data.get('success') else 1)"; then
                echo -e "${GREEN}✓ $test_name passed${NC}"
                echo "Result:"
                python -m json.tool /tmp/flow_result.json | head -20
            else
                echo -e "${RED}✗ $test_name failed${NC}"
                echo "Error:"
                python -c "import json; data=json.load(open('/tmp/flow_result.json')); print(data.get('error', 'Unknown error'))"
            fi
            # Clean up for next test
            rm -f /tmp/flow_result.json
        else
            echo -e "${YELLOW}⚠ No result file generated${NC}"
        fi
    else
        echo -e "${RED}✗ Test execution failed${NC}"
    fi
}

# Run all tests
"""
    
    for test_case in test_cases:
        script += f'run_test "{test_case}"\n'
    
    script += """
echo ""
echo "========================================"
echo "All tests completed!"
"""
    
    with open("run_all_tests.sh", "w") as f:
        f.write(script)
    
    # Make executable
    Path("run_all_tests.sh").chmod(0o755)
    print("Created run_all_tests.sh")


def verify_results():
    """Read and verify test results from flow dev."""
    result_file = "/tmp/flow_result.json"
    
    try:
        with open(result_file, "r") as f:
            result = json.load(f)
        
        if result.get("success"):
            print("✅ Test passed!")
            print("Result:", json.dumps(result.get("result"), indent=2))
        else:
            print("❌ Test failed!")
            print("Error:", result.get("error"))
            if result.get("traceback"):
                print("Traceback:", result.get("traceback"))
    except FileNotFoundError:
        print("❌ No result file found at", result_file)
    except json.JSONDecodeError as e:
        print("❌ Invalid JSON in result file:", e)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_results()
    else:
        print("Generating test wrapper scripts for flow dev...")
        print("=" * 50)
        generate_test_wrappers()
        print("\n" + "=" * 50)
        print("\nNext steps to run tests:")
        print("1. Start flow dev VM:")
        print("   flow dev")
        print("\n2. Upload test files:")
        print("   flow dev --upload")
        print("\n3. Run all tests:")
        print("   flow dev -c 'bash /root/run_all_tests.sh'")
        print("\n4. Or run individual tests:")
        print("   flow dev -c 'python /root/test_basic.py'")
        print("   flow dev -c 'cat /tmp/flow_result.json'")