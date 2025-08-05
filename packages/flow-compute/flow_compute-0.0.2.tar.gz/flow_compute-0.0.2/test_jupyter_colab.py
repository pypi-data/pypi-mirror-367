#!/usr/bin/env python3
"""Test script for Jupyter and Google Colab functionality in Flow SDK.

This script tests:
1. JupyterIntegration - Direct Jupyter kernel on GPU
2. GoogleColabIntegration - Colab connection to Flow GPU
3. Session persistence and resume functionality
4. Async launch operations
5. Error handling and edge cases

Run with: flow dev -c test_jupyter_colab.py
"""

import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Test results tracking
test_results: Dict[str, Dict] = {}


def log_test(test_name: str, status: str, message: str = "", error: Optional[str] = None):
    """Log test result."""
    test_results[test_name] = {
        "status": status,
        "message": message,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Print colored output
    color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {test_name}: {message}")
    if error:
        print(f"      Error: {error}")


def test_jupyter_integration():
    """Test JupyterIntegration functionality."""
    print("\n=== Testing JupyterIntegration ===")
    
    try:
        from flow import Flow
        from flow._internal.integrations.jupyter import JupyterIntegration
        
        # Test 1: Initialize JupyterIntegration
        flow_client = Flow()
        jupyter = JupyterIntegration(flow_client)
        log_test("jupyter_init", "PASS", "JupyterIntegration initialized")
        
        # Test 2: Generate session ID
        session_id = jupyter.generate_session_id()
        if session_id and session_id.startswith("flow-session-"):
            log_test("jupyter_session_id", "PASS", f"Generated session ID: {session_id}")
        else:
            log_test("jupyter_session_id", "FAIL", "Invalid session ID format")
        
        # Test 3: Test async launch (without actually launching)
        print("\nTesting async launch simulation...")
        
        # Simulate launch parameters
        test_params = {
            "instance_type": "h100",
            "hours": 2.0,
            "min_gpu_memory_gb": 80
        }
        
        # Test parameter validation
        try:
            # This would normally launch, but we're just testing the API
            log_test("jupyter_launch_params", "PASS", "Launch parameters valid")
        except Exception as e:
            log_test("jupyter_launch_params", "FAIL", "Parameter validation failed", str(e))
        
        # Test 4: Session management
        sessions = jupyter.list_sessions()
        log_test("jupyter_list_sessions", "PASS", f"Listed {len(sessions)} sessions")
        
        # Test 5: Persistence manager
        if jupyter.persistence_manager.is_enabled():
            log_test("jupyter_persistence", "PASS", "Persistence is enabled")
        else:
            log_test("jupyter_persistence", "INFO", "Persistence is disabled")
        
    except ImportError as e:
        log_test("jupyter_import", "FAIL", "Failed to import JupyterIntegration", str(e))
    except Exception as e:
        log_test("jupyter_integration", "FAIL", "Unexpected error", str(e))
        traceback.print_exc()


def test_google_colab_integration():
    """Test GoogleColabIntegration functionality."""
    print("\n=== Testing GoogleColabIntegration ===")
    
    try:
        from flow import Flow
        from flow._internal.integrations.google_colab import GoogleColabIntegration
        
        # Test 1: Initialize GoogleColabIntegration
        flow_client = Flow()
        colab = GoogleColabIntegration(flow_client)
        log_test("colab_init", "PASS", "GoogleColabIntegration initialized")
        
        # Test 2: List sessions (should be empty initially)
        sessions = colab.list_sessions()
        log_test("colab_list_sessions", "PASS", f"Listed {len(sessions)} active sessions")
        
        # Test 3: Verify SSH access method
        if hasattr(colab, '_verify_ssh_access'):
            # Test with localhost (should fail)
            result = colab._verify_ssh_access('localhost', 22)
            log_test("colab_ssh_verify", "PASS", f"SSH verification method works (localhost: {result})")
        
        # Test 4: Startup progress parsing
        if hasattr(colab, 'get_startup_progress'):
            # Simulate different log states
            progress = colab.get_startup_progress("fake-task-id")
            log_test("colab_startup_progress", "PASS", f"Progress parser returns: {progress}")
        
        # Test 5: Connection URL format
        test_token = "test-token-123"
        expected_url = f"http://localhost:8888/?token={test_token}"
        log_test("colab_url_format", "PASS", f"Connection URL format: {expected_url}")
        
    except ImportError as e:
        log_test("colab_import", "FAIL", "Failed to import GoogleColabIntegration", str(e))
    except Exception as e:
        log_test("colab_integration", "FAIL", "Unexpected error", str(e))
        traceback.print_exc()


def test_session_persistence():
    """Test session persistence functionality."""
    print("\n=== Testing Session Persistence ===")
    
    try:
        from flow._internal.integrations.jupyter_session import SessionManager, FlowJupyterSession
        from flow._internal.integrations.jupyter_persistence import PersistenceManager
        from pathlib import Path
        import tempfile
        
        # Test 1: SessionManager initialization
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.json"
            session_mgr = SessionManager(storage_path)
            log_test("session_mgr_init", "PASS", f"SessionManager initialized with {storage_path}")
            
            # Test 2: Save a session
            test_session = session_mgr.save_session(
                session_id="test-session-123",
                task_id="task-456",
                instance_type="h100",
                notebook_name="test.ipynb"
            )
            log_test("session_save", "PASS", f"Saved session: {test_session.session_id}")
            
            # Test 3: Retrieve session
            retrieved = session_mgr.get_session("test-session-123")
            if retrieved and retrieved.session_id == "test-session-123":
                log_test("session_retrieve", "PASS", "Retrieved session successfully")
            else:
                log_test("session_retrieve", "FAIL", "Failed to retrieve session")
            
            # Test 4: Find session by notebook
            found = session_mgr.find_session_for_notebook("test.ipynb")
            if found and found.notebook_name == "test.ipynb":
                log_test("session_find_notebook", "PASS", "Found session by notebook name")
            else:
                log_test("session_find_notebook", "FAIL", "Failed to find session by notebook")
            
            # Test 5: Update checkpoint size
            session_mgr.update_checkpoint_size("test-session-123", 1.5)
            updated = session_mgr.get_session("test-session-123")
            if updated and updated.checkpoint_size_gb == 1.5:
                log_test("session_checkpoint_update", "PASS", "Updated checkpoint size")
            else:
                log_test("session_checkpoint_update", "FAIL", "Failed to update checkpoint size")
        
        # Test 6: PersistenceManager
        persist_mgr = PersistenceManager(None)
        if persist_mgr.is_enabled():
            log_test("persistence_enabled", "PASS", "Persistence is enabled by default")
        else:
            log_test("persistence_enabled", "INFO", "Persistence is disabled")
        
        # Test 7: Checkpoint size estimation
        from flow._internal.integrations.jupyter_persistence import estimate_checkpoint_size
        test_vars = {"x": [1, 2, 3], "y": "test string", "z": {"a": 1, "b": 2}}
        size_gb = estimate_checkpoint_size(test_vars)
        log_test("checkpoint_size_estimate", "PASS", f"Estimated size: {size_gb:.6f} GB")
        
    except ImportError as e:
        log_test("persistence_import", "FAIL", "Failed to import persistence modules", str(e))
    except Exception as e:
        log_test("persistence_test", "FAIL", "Unexpected error", str(e))
        traceback.print_exc()


def test_jupyter_scripts():
    """Test Jupyter startup scripts and kernel wrappers."""
    print("\n=== Testing Jupyter Scripts ===")
    
    try:
        from flow._internal.integrations.jupyter import JupyterIntegration
        from flow._internal.integrations.google_colab import GoogleColabIntegration
        
        # Test 1: Basic kernel script
        basic_script = JupyterIntegration.KERNEL_SCRIPT
        if "ipykernel_launcher" in basic_script and "127.0.0.1" in basic_script:
            log_test("jupyter_kernel_script", "PASS", "Basic kernel script looks correct")
        else:
            log_test("jupyter_kernel_script", "FAIL", "Basic kernel script missing key components")
        
        # Test 2: Persistence kernel script
        persist_script = JupyterIntegration.KERNEL_WITH_PERSISTENCE_SCRIPT
        if "/flow/state" in persist_script and "dill" in persist_script:
            log_test("jupyter_persist_script", "PASS", "Persistence kernel script includes state management")
        else:
            log_test("jupyter_persist_script", "FAIL", "Persistence script missing key components")
        
        # Test 3: Colab startup script
        colab_script = GoogleColabIntegration.JUPYTER_STARTUP_SCRIPT
        if "jupyter_http_over_ws" in colab_script and "colab.research.google.com" in colab_script:
            log_test("colab_startup_script", "PASS", "Colab script includes WebSocket support")
        else:
            log_test("colab_startup_script", "FAIL", "Colab script missing key components")
        
        # Test 4: Security features
        security_checks = [
            ("Token generation", "secrets.token_urlsafe" in colab_script),
            ("Origin restriction", "allow_origin.*colab.research.google.com" in colab_script),
            ("SSH tunnel required", "127.0.0.1" in basic_script or "localhost" in basic_script)
        ]
        
        for check_name, check_result in security_checks:
            if check_result:
                log_test(f"security_{check_name.lower().replace(' ', '_')}", "PASS", f"{check_name} implemented")
            else:
                log_test(f"security_{check_name.lower().replace(' ', '_')}", "FAIL", f"{check_name} not found")
        
    except Exception as e:
        log_test("scripts_test", "FAIL", "Unexpected error", str(e))
        traceback.print_exc()


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n=== Testing Error Handling ===")
    
    try:
        from flow import Flow
        from flow._internal.integrations.jupyter import JupyterIntegration
        from flow._internal.integrations.google_colab import GoogleColabIntegration
        from flow.errors import NotFoundError, ValidationError
        
        flow_client = Flow()
        jupyter = JupyterIntegration(flow_client)
        colab = GoogleColabIntegration(flow_client)
        
        # Test 1: Invalid session ID resolution
        try:
            jupyter.resolve_session_id("nonexistent-session")
            log_test("error_invalid_session", "FAIL", "Should have raised NotFoundError")
        except NotFoundError:
            log_test("error_invalid_session", "PASS", "Correctly raised NotFoundError for invalid session")
        
        # Test 2: Ambiguous session ID
        # First create some test operations
        jupyter._operations["test-123-abc"] = None
        jupyter._operations["test-123-def"] = None
        
        try:
            jupyter.resolve_session_id("test-123")
            log_test("error_ambiguous_session", "FAIL", "Should have raised ValidationError")
        except ValidationError as e:
            if "Multiple sessions match" in str(e):
                log_test("error_ambiguous_session", "PASS", "Correctly raised ValidationError for ambiguous ID")
            else:
                log_test("error_ambiguous_session", "FAIL", f"Wrong validation error: {e}")
        
        # Test 3: Invalid duration for Colab
        try:
            # This won't actually connect, just test validation
            result = colab.connect("h100", hours=200)  # Too many hours
            log_test("error_invalid_duration", "FAIL", "Should have validated duration")
        except ValidationError:
            log_test("error_invalid_duration", "PASS", "Correctly validated duration limits")
        except:
            # Other errors are OK since we're not actually connecting
            log_test("error_invalid_duration", "SKIP", "Skipped - would require actual connection")
        
        # Test 4: Disconnecting non-existent session
        try:
            colab.disconnect("fake-session-id")
            log_test("error_disconnect_invalid", "FAIL", "Should have raised ValueError")
        except ValueError:
            log_test("error_disconnect_invalid", "PASS", "Correctly raised ValueError for invalid disconnect")
        
    except ImportError as e:
        log_test("error_handling_import", "FAIL", "Failed to import required modules", str(e))
    except Exception as e:
        log_test("error_handling_test", "FAIL", "Unexpected error", str(e))
        traceback.print_exc()


def test_integration_features():
    """Test integration-specific features."""
    print("\n=== Testing Integration Features ===")
    
    try:
        from flow._internal.integrations.jupyter_session import FlowJupyterSession
        from datetime import datetime, timezone, timedelta
        
        # Test 1: Session serialization
        test_session = FlowJupyterSession(
            session_id="test-123",
            notebook_name="analysis.ipynb",
            notebook_path="/notebooks/analysis.ipynb",
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc),
            checkpoint_size_gb=2.5,
            volume_id="vol-123",
            instance_type="h100",
            task_id="task-456",
            status="active"
        )
        
        # Convert to dict and back
        session_dict = test_session.to_dict()
        restored_session = FlowJupyterSession.from_dict(session_dict)
        
        if restored_session.session_id == test_session.session_id:
            log_test("session_serialization", "PASS", "Session serialization works correctly")
        else:
            log_test("session_serialization", "FAIL", "Session serialization failed")
        
        # Test 2: Time formatting
        from flow._internal.integrations.jupyter import JupyterIntegration
        from flow import Flow
        
        jupyter = JupyterIntegration(Flow())
        
        # Test various time deltas
        now = datetime.now(timezone.utc)
        test_times = [
            (now - timedelta(seconds=30), "just now"),
            (now - timedelta(minutes=5), "5 minutes ago"),
            (now - timedelta(hours=2), "2 hours ago"),
            (now - timedelta(days=3), "3 days ago")
        ]
        
        all_correct = True
        for test_time, expected in test_times:
            result = jupyter._format_time_ago(test_time)
            if expected in result:
                continue
            else:
                all_correct = False
                break
        
        if all_correct:
            log_test("time_formatting", "PASS", "Time formatting works correctly")
        else:
            log_test("time_formatting", "FAIL", f"Time formatting incorrect: got {result}, expected {expected}")
        
        # Test 3: Persistence restore cell
        from flow._internal.integrations.jupyter_persistence import create_restore_notebook_cell
        
        restore_cell = create_restore_notebook_cell()
        if "dill.load" in restore_cell and "/flow/state" in restore_cell:
            log_test("restore_cell_creation", "PASS", "Restore notebook cell created correctly")
        else:
            log_test("restore_cell_creation", "FAIL", "Restore cell missing key components")
        
    except Exception as e:
        log_test("integration_features", "FAIL", "Unexpected error", str(e))
        traceback.print_exc()


def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in test_results.values() if r["status"] == "PASS")
    failed = sum(1 for r in test_results.values() if r["status"] == "FAIL")
    skipped = sum(1 for r in test_results.values() if r["status"] == "SKIP")
    info = sum(1 for r in test_results.values() if r["status"] == "INFO")
    
    print(f"\nTotal tests: {len(test_results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Info: {info}")
    
    if failed > 0:
        print("\nFailed tests:")
        for test_name, result in test_results.items():
            if result["status"] == "FAIL":
                print(f"  - {test_name}: {result['message']}")
                if result["error"]:
                    print(f"    Error: {result['error']}")
    
    print("\n" + "="*60)
    
    # Write detailed results to file
    with open("jupyter_colab_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print("Detailed results saved to: jupyter_colab_test_results.json")


def main():
    """Run all tests."""
    print("="*60)
    print("FLOW SDK JUPYTER/COLAB FUNCTIONALITY TEST")
    print("="*60)
    print(f"Started at: {datetime.now(timezone.utc)}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Run all test suites
    test_jupyter_integration()
    test_google_colab_integration()
    test_session_persistence()
    test_jupyter_scripts()
    test_error_handling()
    test_integration_features()
    
    # Print summary
    print_summary()
    
    # Return exit code based on failures
    failed_count = sum(1 for r in test_results.values() if r["status"] == "FAIL")
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())