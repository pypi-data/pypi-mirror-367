
import json
import sys
import traceback

def test_basic(x: int, y: int = 10):
    """Basic test function."""
    return {"sum": x + y, "product": x * y}

# Execute with provided arguments
args = [5]
kwargs = {"y": 20}

try:
    result = test_basic(*args, **kwargs)
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({"success": True, "result": result}, f)
    print(f"✅ Test completed: sum={result['sum']}, product={result['product']}")
except Exception as e:
    tb = traceback.format_exc()
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": tb
        }, f)
    print(f"❌ Test failed: {e}")
    raise
