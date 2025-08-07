#!/bin/bash
# Test runner for decorator functionality with flow dev

set -e  # Exit on error

echo "Starting decorator tests on flow dev VM..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run a test and check result
run_test() {
    local test_file=$1
    local test_name=$(basename $test_file .py)
    
    echo ""
    echo "Running test: $test_name"
    echo "------------------------"
    
    # Run the test
    if python /root/$test_file; then
        # Check if result file exists
        if [ -f /tmp/flow_result.json ]; then
            # Parse result
            if python -c "import json; data=json.load(open('/tmp/flow_result.json')); exit(0 if data.get('success') else 1)"; then
                echo -e "${GREEN}✓ $test_name passed${NC}"
                echo "Result:"
                python -m json.tool /tmp/flow_result.json | head -20
            else
                echo -e "${RED}✗ $test_name failed${NC}"
                echo "Error:"
                python -c "import json; data=json.load(open('/tmp/flow_result.json')); print(data.get('error', 'Unknown error'))"
            fi
            # Clean up for next test
            rm -f /tmp/flow_result.json
        else
            echo -e "${YELLOW}⚠ No result file generated${NC}"
        fi
    else
        echo -e "${RED}✗ Test execution failed${NC}"
    fi
}

# Run all tests
run_test "test_basic.py"
run_test "test_gpu.py"
run_test "test_volumes.py"
run_test "test_environment.py"
run_test "test_retries.py"
run_test "test_timeout.py"
run_test "test_complex_args.py"
run_test "test_all_params.py"

echo ""
echo "========================================"
echo "All tests completed!"
