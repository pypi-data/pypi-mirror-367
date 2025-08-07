#!/usr/bin/env python
"""Simple test to verify decorator functionality step by step.

This creates a minimal test case that's easy to debug.
"""

from flow import FlowApp
from flow.api.models import Retries
import json


def create_simple_test():
    """Create a simple test function with decorator."""
    app = FlowApp()
    
    @app.function(
        gpu="a100",
        memory=32768,
        image="python:3.11",
        environment={"TEST_ENV": "flow_dev_test"}
    )
    def simple_add(x: int, y: int = 10) -> dict:
        """Simple test function that adds two numbers."""
        import os
        return {
            "sum": x + y,
            "product": x * y,
            "env_var": os.environ.get("TEST_ENV", "not_set"),
            "test": "decorator_works"
        }
    
    # Generate wrapper script
    wrapper = simple_add._create_wrapper_script((5,), {"y": 15})
    
    # Fix imports for standalone execution
    wrapper = wrapper.replace(
        "from test_decorator_simple import simple_add",
        """
def simple_add(x: int, y: int = 10) -> dict:
    import os
    return {
        "sum": x + y,
        "product": x * y,
        "env_var": os.environ.get("TEST_ENV", "not_set"),
        "test": "decorator_works"
    }
"""
    )
    
    # Save wrapper
    with open("wrapper_test.py", "w") as f:
        f.write(wrapper)
    
    print("Created wrapper_test.py")
    print("\nWrapper content preview:")
    print("=" * 50)
    print(wrapper[:500])
    print("..." if len(wrapper) > 500 else "")
    print("=" * 50)
    
    return wrapper


if __name__ == "__main__":
    print("Creating simple decorator test...")
    create_simple_test()
    
    print("\n📋 Commands to run this test:\n")
    print("# 1. Generate the wrapper (you just did this)")
    print("python test_decorator_simple.py\n")
    
    print("# 2. Start or connect to flow dev VM")
    print("flow dev\n")
    
    print("# 3. Upload the wrapper to the VM")
    print("flow dev --upload\n")
    
    print("# 4. Run the wrapper on the VM")
    print("flow dev -c 'python /root/wrapper_test.py'\n")
    
    print("# 5. Check the results")
    print("flow dev -c 'cat /tmp/flow_result.json'\n")
    
    print("# 6. Pretty print the results")
    print("flow dev -c 'python -m json.tool /tmp/flow_result.json'\n")
    
    print("\n✅ Expected result:")
    expected = {
        "success": True,
        "result": {
            "sum": 20,
            "product": 75,
            "env_var": "not_set",  # Will be "flow_dev_test" if env vars work
            "test": "decorator_works"
        }
    }
    print(json.dumps(expected, indent=2))