
import json
import sys
import traceback

def test_error_handling(should_fail=False):
    """Test error handling in wrapper."""
    if should_fail:
        raise ValueError("Intentional test error to verify error handling")
    return {"status": "success", "error_handling": "working"}

# Test both success and failure
try:
    # First test success
    result = test_error_handling(False)
    print(f"✅ Success case passed")
    
    # Now test failure
    try:
        test_error_handling(True)
        print(f"❌ Should have raised an error")
    except ValueError as e:
        print(f"✅ Error handling working: {e}")
        result["error_caught"] = str(e)
    
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({"success": True, "result": result}, f)
    
except Exception as e:
    tb = traceback.format_exc()
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({
            "success": False,
            "error": str(e),
            "traceback": tb
        }, f)
    print(f"❌ Unexpected error: {e}")
    raise
