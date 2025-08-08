#!/usr/bin/env python3
"""Live test script for Docker functionality on real flow dev VMs.

This script tests Docker integration by:
1. Starting a real flow dev VM
2. Running Docker commands on the VM
3. Testing different Docker images and configurations
4. Verifying container isolation
5. Testing GPU support if available

Requirements:
- Flow SDK installed and configured
- Valid Flow API credentials
- Network connectivity to provision VMs

Usage:
    python test_flow_dev_docker_live.py [--instance-type TYPE] [--cleanup]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class FlowDevDockerTester:
    """Test Docker functionality on real flow dev VMs."""
    
    def __init__(self, instance_type: str = "h100", cleanup: bool = True):
        """Initialize tester.
        
        Args:
            instance_type: Instance type for the dev VM
            cleanup: Whether to stop the VM after tests
        """
        self.instance_type = instance_type
        self.cleanup = cleanup
        self.test_results = []
        self.vm_started = False
        
    def run_command(self, cmd: str, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a shell command and return the result.
        
        Args:
            cmd: Command to run
            capture_output: Whether to capture output
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        print(f"{BLUE}Running: {cmd}{RESET}")
        
        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        else:
            # For interactive commands
            result = subprocess.run(cmd, shell=True)
            return result.returncode, "", ""
    
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record a test result.
        
        Args:
            test_name: Name of the test
            passed: Whether the test passed
            details: Additional details about the test
        """
        status = f"{GREEN}✓ PASSED{RESET}" if passed else f"{RED}✗ FAILED{RESET}"
        print(f"\n{status}: {test_name}")
        if details:
            print(f"  Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def start_dev_vm(self) -> bool:
        """Start the flow dev VM.
        
        Returns:
            True if VM started successfully
        """
        print(f"\n{BOLD}Starting flow dev VM...{RESET}")
        print(f"Instance type: {self.instance_type}")
        
        # First check if there's already a dev VM running
        ret, stdout, stderr = self.run_command("flow dev --status")
        if "Status: running" in stdout:
            print(f"{YELLOW}Dev VM already running, using existing VM{RESET}")
            self.vm_started = False  # Don't cleanup if we didn't start it
            return True
        
        # Start new dev VM
        cmd = f"flow dev --instance-type {self.instance_type} -c 'echo VM started'"
        ret, stdout, stderr = self.run_command(cmd)
        
        if ret == 0:
            print(f"{GREEN}Dev VM started successfully{RESET}")
            self.vm_started = True
            # Give VM a moment to fully initialize
            time.sleep(5)
            return True
        else:
            print(f"{RED}Failed to start dev VM{RESET}")
            print(f"Error: {stderr}")
            return False
    
    def test_docker_installation(self) -> bool:
        """Test that Docker is installed on the VM.
        
        Returns:
            True if Docker is installed
        """
        print(f"\n{BOLD}Testing Docker installation...{RESET}")
        
        # Check Docker version
        ret, stdout, stderr = self.run_command("flow dev -c 'docker --version'")
        
        if ret == 0 and "Docker version" in stdout:
            docker_version = stdout.strip()
            self.test_result(
                "Docker Installation",
                True,
                f"Docker is installed: {docker_version}"
            )
            return True
        else:
            self.test_result(
                "Docker Installation",
                False,
                f"Docker not found or not working: {stderr}"
            )
            return False
    
    def test_docker_daemon(self) -> bool:
        """Test that Docker daemon is running.
        
        Returns:
            True if Docker daemon is running
        """
        print(f"\n{BOLD}Testing Docker daemon...{RESET}")
        
        # Check Docker daemon status
        ret, stdout, stderr = self.run_command("flow dev -c 'docker info'")
        
        if ret == 0:
            # Extract some info from docker info
            lines = stdout.split('\n')
            server_version = next((l for l in lines if 'Server Version:' in l), '')
            storage_driver = next((l for l in lines if 'Storage Driver:' in l), '')
            
            self.test_result(
                "Docker Daemon",
                True,
                f"Docker daemon is running. {server_version}, {storage_driver}"
            )
            return True
        else:
            self.test_result(
                "Docker Daemon",
                False,
                f"Docker daemon not running: {stderr}"
            )
            return False
    
    def test_default_environment(self) -> bool:
        """Test default environment (no container).
        
        Returns:
            True if default environment works
        """
        print(f"\n{BOLD}Testing default environment (no container)...{RESET}")
        
        # Install a package directly on VM
        ret1, _, _ = self.run_command("flow dev -c 'pip install requests --quiet'")
        
        # Use the package
        ret2, stdout, _ = self.run_command(
            "flow dev -c 'python -c \"import requests; print(requests.__version__)\"'"
        )
        
        success = ret1 == 0 and ret2 == 0 and stdout.strip()
        
        self.test_result(
            "Default Environment (No Container)",
            success,
            f"Package installed and imported successfully: requests {stdout.strip()}" if success else "Failed to install/use package"
        )
        
        return success
    
    def test_docker_images(self) -> bool:
        """Test pulling and running different Docker images.
        
        Returns:
            True if Docker images work
        """
        print(f"\n{BOLD}Testing Docker images...{RESET}")
        
        test_images = [
            ("alpine:latest", "echo 'Hello from Alpine'", "Alpine Linux"),
            ("python:3.11-slim", "python --version", "Python container"),
            ("ubuntu:22.04", "cat /etc/os-release | grep VERSION", "Ubuntu container"),
        ]
        
        all_passed = True
        
        for image, command, description in test_images:
            print(f"\nTesting {description} ({image})...")
            
            # Pull and run the image
            docker_cmd = f"docker run --rm {image} {command}"
            ret, stdout, stderr = self.run_command(f"flow dev -c '{docker_cmd}'")
            
            success = ret == 0 and stdout
            all_passed = all_passed and success
            
            self.test_result(
                f"Docker Image: {image}",
                success,
                f"Output: {stdout.strip()}" if success else f"Error: {stderr}"
            )
        
        return all_passed
    
    def test_named_environments(self) -> bool:
        """Test named environments with container isolation.
        
        Returns:
            True if named environments work
        """
        print(f"\n{BOLD}Testing named environments (container isolation)...{RESET}")
        
        # Create two different environments
        environments = [
            ("python-env", "python:3.11-slim", "pip install numpy && python -c 'import numpy; print(f\"NumPy {numpy.__version__}\")'"),
            ("node-env", "node:18-slim", "npm --version && node --version"),
        ]
        
        all_passed = True
        
        for env_name, image, command in environments:
            print(f"\nTesting environment: {env_name} with {image}...")
            
            # Run command in named environment
            ret, stdout, stderr = self.run_command(
                f"flow dev -e {env_name} --image {image} -c '{command}'"
            )
            
            success = ret == 0 and stdout
            all_passed = all_passed and success
            
            self.test_result(
                f"Named Environment: {env_name}",
                success,
                f"Output: {stdout.strip()}" if success else f"Error: {stderr}"
            )
        
        # Test isolation - numpy should not be in node-env
        print(f"\nTesting environment isolation...")
        ret, stdout, stderr = self.run_command(
            "flow dev -e node-env --image python:3.11-slim -c 'python -c \"import numpy\"' 2>&1"
        )
        
        # This should fail (numpy not installed in node-env)
        isolation_works = "ModuleNotFoundError" in stdout or "ModuleNotFoundError" in stderr or ret != 0
        
        self.test_result(
            "Environment Isolation",
            isolation_works,
            "Environments are properly isolated" if isolation_works else "Environments may not be isolated"
        )
        
        return all_passed and isolation_works
    
    def test_gpu_docker(self) -> bool:
        """Test GPU support in Docker containers.
        
        Returns:
            True if GPU Docker support works
        """
        print(f"\n{BOLD}Testing GPU Docker support...{RESET}")
        
        # Check if this is a GPU instance
        ret, stdout, _ = self.run_command("flow dev -c 'nvidia-smi -L 2>/dev/null'")
        
        if ret != 0 or not stdout:
            print(f"{YELLOW}Skipping GPU tests - no GPU detected{RESET}")
            return True  # Not a failure, just skip
        
        print("GPU detected, testing Docker GPU support...")
        
        # Test with NVIDIA CUDA image
        docker_cmd = (
            "docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 "
            "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"
        )
        
        ret, stdout, stderr = self.run_command(f"flow dev -c '{docker_cmd}'")
        
        success = ret == 0 and stdout
        
        self.test_result(
            "GPU Docker Support",
            success,
            f"GPU accessible in container: {stdout.strip()}" if success else f"GPU not accessible: {stderr}"
        )
        
        return success
    
    def test_volume_mounts(self) -> bool:
        """Test volume mounting in Docker containers.
        
        Returns:
            True if volume mounts work
        """
        print(f"\n{BOLD}Testing Docker volume mounts...{RESET}")
        
        # Create a test file on the host
        test_file_content = f"Test file created at {datetime.now()}"
        create_file_cmd = f"echo '{test_file_content}' > /tmp/test_mount.txt"
        
        ret1, _, _ = self.run_command(f"flow dev -c '{create_file_cmd}'")
        
        # Read the file from a Docker container with volume mount
        docker_cmd = (
            "docker run --rm -v /tmp:/host_tmp:ro alpine:latest "
            "cat /host_tmp/test_mount.txt"
        )
        
        ret2, stdout, _ = self.run_command(f"flow dev -c '{docker_cmd}'")
        
        success = ret1 == 0 and ret2 == 0 and test_file_content in stdout
        
        self.test_result(
            "Docker Volume Mounts",
            success,
            "Volume mounting works correctly" if success else "Volume mounting failed"
        )
        
        # Clean up test file
        self.run_command("flow dev -c 'rm -f /tmp/test_mount.txt'")
        
        return success
    
    def test_docker_networking(self) -> bool:
        """Test Docker networking.
        
        Returns:
            True if Docker networking works
        """
        print(f"\n{BOLD}Testing Docker networking...{RESET}")
        
        # Test network connectivity from container
        docker_cmd = "docker run --rm alpine:latest ping -c 2 8.8.8.8"
        ret, stdout, _ = self.run_command(f"flow dev -c '{docker_cmd}'")
        
        success = ret == 0 and "2 packets transmitted, 2 packets received" in stdout
        
        self.test_result(
            "Docker Networking",
            success,
            "Container can reach external network" if success else "Network connectivity failed"
        )
        
        return success
    
    def test_container_persistence(self) -> bool:
        """Test that named environment data persists.
        
        Returns:
            True if persistence works
        """
        print(f"\n{BOLD}Testing container data persistence...{RESET}")
        
        env_name = "persist-test"
        
        # Create a file in named environment
        ret1, _, _ = self.run_command(
            f"flow dev -e {env_name} -c 'echo \"persistent data\" > /workspace/test.txt'"
        )
        
        # Read the file in a second run
        ret2, stdout, _ = self.run_command(
            f"flow dev -e {env_name} -c 'cat /workspace/test.txt'"
        )
        
        success = ret1 == 0 and ret2 == 0 and "persistent data" in stdout
        
        self.test_result(
            "Container Data Persistence",
            success,
            "Data persists in named environments" if success else "Data persistence failed"
        )
        
        return success
    
    def cleanup_vm(self):
        """Stop the dev VM if we started it."""
        if self.cleanup and self.vm_started:
            print(f"\n{BOLD}Cleaning up...{RESET}")
            ret, _, _ = self.run_command("flow dev --stop")
            if ret == 0:
                print(f"{GREEN}Dev VM stopped{RESET}")
            else:
                print(f"{YELLOW}Failed to stop dev VM{RESET}")
    
    def run_all_tests(self) -> bool:
        """Run all Docker tests.
        
        Returns:
            True if all tests passed
        """
        print(f"\n{'=' * 60}")
        print(f"{BOLD}Flow Dev Docker Live Testing{RESET}")
        print(f"{'=' * 60}")
        print(f"Instance Type: {self.instance_type}")
        print(f"Timestamp: {datetime.now()}")
        
        # Start VM
        if not self.start_dev_vm():
            print(f"{RED}Failed to start dev VM, aborting tests{RESET}")
            return False
        
        # Run tests
        tests = [
            self.test_docker_installation,
            self.test_docker_daemon,
            self.test_default_environment,
            self.test_docker_images,
            self.test_named_environments,
            self.test_gpu_docker,
            self.test_volume_mounts,
            self.test_docker_networking,
            self.test_container_persistence,
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                test_name = test_func.__name__.replace("test_", "").replace("_", " ").title()
                self.test_result(test_name, False, f"Exception: {e}")
        
        # Print summary
        print(f"\n{'=' * 60}")
        print(f"{BOLD}Test Summary{RESET}")
        print(f"{'=' * 60}")
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = f"{GREEN}✓{RESET}" if result["passed"] else f"{RED}✗{RESET}"
            print(f"{status} {result['test']}")
        
        print(f"\n{BOLD}Results: {passed}/{total} tests passed{RESET}")
        
        all_passed = passed == total
        if all_passed:
            print(f"{GREEN}🎉 All tests passed!{RESET}")
        else:
            print(f"{RED}⚠️  Some tests failed{RESET}")
        
        # Cleanup
        self.cleanup_vm()
        
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Docker functionality on real flow dev VMs"
    )
    parser.add_argument(
        "--instance-type",
        default="h100",
        help="Instance type for the dev VM (default: h100)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't stop the VM after tests"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only essential tests"
    )
    
    args = parser.parse_args()
    
    # Check if flow is installed
    ret = subprocess.run("flow --version", shell=True, capture_output=True)
    if ret.returncode != 0:
        print(f"{RED}Error: Flow CLI not found. Please install Flow SDK first.{RESET}")
        sys.exit(1)
    
    # Run tests
    tester = FlowDevDockerTester(
        instance_type=args.instance_type,
        cleanup=not args.no_cleanup
    )
    
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()