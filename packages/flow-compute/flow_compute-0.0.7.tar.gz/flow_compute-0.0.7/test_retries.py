
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from __main__ import test_retries

args_data = json.loads('"{\\"args\\": [1], \\"kwargs\\": {}}"')
args = args_data["args"]
kwargs = args_data["kwargs"]

try:
    result = test_retries(*args, **kwargs)
    
    # Result must be JSON-serializable
    try:
        json.dumps(result)
    except (TypeError, ValueError) as e:
        # Provide guidance if result is not JSON-serializable
        raise TypeError(
            f"Function returned non-JSON-serializable result: {type(result).__name__}\n"
            f"\n"
            f"Functions must return JSON-serializable values:\n"
            f"  - Basic types: str, int, float, bool, None\n"
            f"  - Collections: list, dict (with JSON-serializable values)\n"
            f"  - File paths: Return paths to saved outputs\n"
            f"\n"
            f"For complex outputs, save to disk and return the path:\n"
            f"  def test_retries(...):\n"
            f"      # Process data...\n"
            f"      np.save('/outputs/result.npy', result_array)\n"
            f"      return {'result_path': '/outputs/result.npy', 'metrics': {...}}\n"
        ) from e
    
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({"success": True, "result": result}, f)
        
except Exception as e:
    # Capture full traceback for better debugging
    tb = traceback.format_exc()
    error_info = {
        "success": False,
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": tb
    }
    
    with open("/tmp/flow_result.json", "w") as f:
        json.dump(error_info, f)
    
    # Still raise to ensure non-zero exit code
    raise

# Ensure the script runs when executed directly
if __name__ == "__main__":
    print(f"Test {__file__} completed. Check /tmp/flow_result.json for results.")
