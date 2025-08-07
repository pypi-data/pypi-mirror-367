
import json
import sys
import traceback
import os
import platform

def test_gpu_env():
    """Test GPU configuration and environment."""
    result = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "env_vars": {
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "not_set"),
            "PATH": os.environ.get("PATH", "")[:100]
        }
    }
    
    # Try to check GPU availability
    try:
        import torch
        result["torch_version"] = torch.__version__
        result["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            result["gpu_count"] = torch.cuda.device_count()
            result["gpu_name"] = torch.cuda.get_device_name(0)
    except ImportError:
        result["torch_available"] = False
    
    return result

try:
    result = test_gpu_env()
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({"success": True, "result": result}, f)
    print(f"✅ GPU test completed")
    print(f"   Python: {result['python_version']}")
    if 'torch_version' in result:
        print(f"   PyTorch: {result['torch_version']}")
        print(f"   CUDA available: {result.get('cuda_available', False)}")
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
