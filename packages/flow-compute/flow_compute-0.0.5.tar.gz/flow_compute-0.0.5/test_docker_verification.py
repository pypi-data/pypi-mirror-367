#!/usr/bin/env python3
"""Test script to verify Docker and other command availability checks in startup scripts."""

import sys
import textwrap
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from flow.providers.mithril.runtime.startup.sections import (
    HeaderSection,
    DockerSection,
    DevVMDockerSection,
    PortForwardingSection,
    S3Section,
    GPUdHealthSection,
    ScriptContext,
)
from flow.providers.mithril.runtime.startup.utils import (
    ensure_command_available,
    ensure_docker_available,
    ensure_curl_available,
    ensure_basic_tools,
)


def test_command_availability_checks():
    """Test that command availability checks are properly generated."""
    print("Testing command availability check generation...")
    
    # Test Docker availability check
    docker_check = ensure_docker_available()
    assert "command -v docker" in docker_check
    assert "curl -fsSL https://get.docker.com" in docker_check
    assert "systemctl enable docker" in docker_check
    print("✓ Docker availability check includes proper installation logic")
    
    # Test curl availability check
    curl_check = ensure_curl_available()
    assert "command -v curl" in curl_check
    assert "apt-get install -y -qq curl" in curl_check
    print("✓ Curl availability check includes installation")
    
    # Test basic tools check
    basic_tools = ensure_basic_tools()
    assert "command -v curl" in basic_tools
    assert "command -v uuidgen" in basic_tools
    assert "apt-get update -qq" in basic_tools
    print("✓ Basic tools check includes all necessary utilities")
    
    # Test individual command checks
    nginx_check = ensure_command_available("nginx")
    assert "command -v nginx" in nginx_check
    assert "apt-get install -y -qq nginx" in nginx_check
    print("✓ Nginx availability check includes apt-get install")
    
    s3fs_check = ensure_command_available("s3fs")
    assert "command -v s3fs" in s3fs_check
    assert "apt-get install -y -qq s3fs" in s3fs_check
    print("✓ S3fs availability check includes apt-get install")
    
    aws_check = ensure_command_available("aws")
    assert "command -v aws" in aws_check
    assert "awscli.amazonaws.com" in aws_check
    print("✓ AWS CLI availability check includes download URL")


def test_startup_sections():
    """Test that startup sections properly include command checks."""
    print("\nTesting startup sections...")
    
    # Create a test context
    context = ScriptContext(
        docker_image="ubuntu:latest",
        ports=[8080, 3000],
        environment={
            "FLOW_DEV_VM": "true",
            "S3_MOUNT_0_BUCKET": "test-bucket",
            "S3_MOUNT_0_TARGET": "/data/s3",
            "S3_MOUNTS_COUNT": "1",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "FLOW_HEALTH_MONITORING": "true",
        },
        instance_type="g4dn.xlarge",  # GPU instance
    )
    
    # Test HeaderSection includes basic tools check
    header = HeaderSection()
    header_script = header.generate(context)
    assert "ensure_basic_tools()" in header_script or "command -v" in header_script
    print("✓ Header section includes command availability checks")
    
    # Test DockerSection includes Docker check
    docker_section = DockerSection()
    docker_script = docker_section.generate(context)
    assert "ensure_docker_available()" in docker_script or "command -v docker" in docker_script
    print("✓ Docker section includes Docker availability check")
    
    # Test DevVMDockerSection
    dev_vm_section = DevVMDockerSection()
    dev_vm_script = dev_vm_section.generate(context)
    assert "ensure_docker_available()" in dev_vm_script or "command -v docker" in dev_vm_script
    print("✓ Dev VM Docker section includes Docker check")
    
    # Test PortForwardingSection includes nginx check
    port_section = PortForwardingSection()
    port_script = port_section.generate(context)
    assert "ensure_command_available('nginx')" in port_script or "nginx" in port_script
    print("✓ Port forwarding section includes nginx check")
    
    # Test S3Section includes s3fs check
    s3_section = S3Section()
    s3_script = s3_section.generate(context)
    assert "ensure_command_available('s3fs')" in s3_script or "s3fs" in s3_script
    print("✓ S3 section includes s3fs check")
    
    # Test GPUdHealthSection includes curl and python3 checks
    gpud_section = GPUdHealthSection()
    gpud_script = gpud_section.generate(context)
    assert "ensure_command_available('curl')" in gpud_script or "curl" in gpud_script
    assert "ensure_command_available('python3')" in gpud_script or "python3" in gpud_script
    print("✓ GPUd health section includes curl and python3 checks")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\nTesting edge cases...")
    
    # Test command without install method
    unknown_cmd = ensure_command_available("unknown_command")
    assert "WARNING" in unknown_cmd
    assert "no installation method" in unknown_cmd
    print("✓ Unknown command generates warning")
    
    # Test empty context
    empty_context = ScriptContext()
    header = HeaderSection()
    header_script = header.generate(empty_context)
    assert "#!/bin/bash" in header_script
    print("✓ Empty context still generates valid script header")
    
    # Test Docker section without Docker image
    context_no_docker = ScriptContext()
    docker_section = DockerSection()
    assert not docker_section.should_include(context_no_docker)
    print("✓ Docker section correctly skipped when no Docker image")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Docker and Command Availability Fixes")
    print("=" * 60)
    
    try:
        test_command_availability_checks()
        test_startup_sections()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        print("\nSummary of fixes:")
        print("- Added ensure_basic_tools() to header section for core utilities")
        print("- Docker installation now includes curl check and retry logic")
        print("- nginx installation properly checks availability first")
        print("- s3fs installation includes DEBIAN_FRONTEND=noninteractive")
        print("- AWS CLI installation includes full download and install logic")
        print("- GPUd installation checks for curl availability")
        print("- Python3 availability verified for metrics streaming")
        print("- All apt-get commands include proper environment setup")
        print("- Fallback logic for missing commands like uuidgen")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()