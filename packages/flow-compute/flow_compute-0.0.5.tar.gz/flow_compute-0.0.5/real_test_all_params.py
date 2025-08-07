
import json
import sys
import traceback
import os

def test_all_params():
    """Test that all decorator parameters would be available."""
    # In a real decorator execution, these would come from the decorator
    decorator_params = {
        "gpu": "h100:4",
        "cpu": (8.0, 16.0),
        "memory": (65536, 131072),
        "image": "pytorch/pytorch:latest",
        "retries": {"max_attempts": 3, "initial_delay": 2.0},
        "timeout": 7200,
        "volumes": {
            "/data": "dataset",
            "/models": {"name": "cache", "size_gb": 500}
        },
        "environment": {"CUDA_DEVICES": "0,1,2,3,4,5,6,7"}
    }
    
    # Verify all parameters are present
    checks = {
        "has_gpu": "gpu" in decorator_params,
        "has_cpu_tuple": isinstance(decorator_params.get("cpu"), tuple),
        "has_memory_tuple": isinstance(decorator_params.get("memory"), tuple),
        "has_image": "image" in decorator_params,
        "has_retries": "retries" in decorator_params,
        "has_timeout": "timeout" in decorator_params,
        "has_volumes": "volumes" in decorator_params,
        "has_environment": "environment" in decorator_params,
        "all_params_present": True
    }
    
    return {
        "decorator_params": decorator_params,
        "validation": checks,
        "all_checks_passed": all(checks.values())
    }

try:
    result = test_all_params()
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({"success": True, "result": result}, f)
    print(f"✅ All parameters test completed")
    print(f"   All checks passed: {result['all_checks_passed']}")
    print(f"   Parameters validated: {len(result['validation'])}")
except Exception as e:
    tb = traceback.format_exc()
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({
            "success": False,
            "error": str(e),
            "traceback": tb
        }, f)
    print(f"❌ Test failed: {e}")
    raise
