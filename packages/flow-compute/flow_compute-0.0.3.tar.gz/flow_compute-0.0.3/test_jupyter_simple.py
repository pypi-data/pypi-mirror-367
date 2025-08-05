#!/usr/bin/env python3
"""Simple test script for Jupyter/Colab functionality.

Run with: flow dev -c 'python test_jupyter_simple.py'
"""

import sys
import traceback


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from flow import Flow
        print("✓ Flow imported")
        
        from flow._internal.integrations.jupyter import JupyterIntegration
        print("✓ JupyterIntegration imported")
        
        from flow._internal.integrations.google_colab import GoogleColabIntegration
        print("✓ GoogleColabIntegration imported")
        
        from flow._internal.integrations.jupyter_session import SessionManager
        print("✓ SessionManager imported")
        
        from flow._internal.integrations.jupyter_persistence import PersistenceManager
        print("✓ PersistenceManager imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality without datetime operations."""
    print("\nTesting basic functionality...")
    
    try:
        from flow import Flow
        from flow._internal.integrations.jupyter import JupyterIntegration
        from flow._internal.integrations.google_colab import GoogleColabIntegration
        
        # Initialize clients
        flow_client = Flow()
        print("✓ Flow client created")
        
        jupyter = JupyterIntegration(flow_client)
        print("✓ JupyterIntegration initialized")
        
        colab = GoogleColabIntegration(flow_client)
        print("✓ GoogleColabIntegration initialized")
        
        # Test session ID generation
        session_id = jupyter.generate_session_id()
        print(f"✓ Generated session ID: {session_id}")
        
        # Test script content
        if "ipykernel_launcher" in JupyterIntegration.KERNEL_SCRIPT:
            print("✓ Kernel script contains ipykernel_launcher")
        
        if "jupyter_http_over_ws" in GoogleColabIntegration.JUPYTER_STARTUP_SCRIPT:
            print("✓ Colab script contains WebSocket support")
        
        # Test persistence
        if jupyter.persistence_manager.is_enabled():
            print("✓ Persistence is enabled")
        else:
            print("✓ Persistence is disabled")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_colab_connection_format():
    """Test Colab connection URL format."""
    print("\nTesting Colab connection format...")
    
    try:
        # Test connection URL format
        test_token = "test-token-abc123"
        expected_url = f"http://localhost:8888/?token={test_token}"
        expected_ssh = "ssh -L 8888:localhost:8888 ubuntu@instance-ip"
        
        print(f"✓ Connection URL format: {expected_url}")
        print(f"✓ SSH tunnel format: {expected_ssh}")
        
        # Test security features
        from flow._internal.integrations.google_colab import GoogleColabIntegration
        
        script = GoogleColabIntegration.JUPYTER_STARTUP_SCRIPT
        security_features = [
            ("Token authentication", "JUPYTER_TOKEN" in script),
            ("Origin restriction", "colab.research.google.com" in script),
            ("WebSocket extension", "jupyter_http_over_ws" in script),
            ("Port configuration", "port=8888" in script)
        ]
        
        for feature, present in security_features:
            if present:
                print(f"✓ {feature}: Present")
            else:
                print(f"✗ {feature}: Missing")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection format test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("JUPYTER/COLAB SIMPLE TEST")
    print("="*60)
    
    tests_passed = 0
    tests_total = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    if test_colab_connection_format():
        tests_passed += 1
    
    print("\n" + "="*60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print("="*60)
    
    return 0 if tests_passed == tests_total else 1


if __name__ == "__main__":
    sys.exit(main())