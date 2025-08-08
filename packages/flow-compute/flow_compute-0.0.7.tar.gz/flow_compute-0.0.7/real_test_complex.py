
import json
import sys
import traceback

def test_complex_args(numbers, config, threshold=0.5):
    """Test complex argument types."""
    return {
        "sum_numbers": sum(numbers),
        "config_keys": list(config.keys()),
        "threshold": threshold,
        "types_ok": {
            "numbers_is_list": isinstance(numbers, list),
            "config_is_dict": isinstance(config, dict),
            "threshold_is_float": isinstance(threshold, float)
        }
    }

# Test with complex arguments
args = [[1, 2, 3, 4, 5]]
kwargs = {
    "config": {"learning_rate": 0.001, "batch_size": 32},
    "threshold": 0.8
}

try:
    result = test_complex_args(*args, **kwargs)
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({"success": True, "result": result}, f)
    print(f"✅ Complex args test passed")
    print(f"   Sum: {result['sum_numbers']}")
    print(f"   Config keys: {result['config_keys']}")
    print(f"   Types validated: {all(result['types_ok'].values())}")
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
