#!/bin/bash
# Run all decorator tests on flow dev

echo "🚀 Running Flow Decorator Tests on Dev VM"
echo "=========================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test runner function
run_test() {
    local test_file=$1
    echo ""
    echo "📝 Running: $test_file"
    echo "-------------------"
    
    if python /root/$test_file; then
        echo -e "${GREEN}✅ Test passed${NC}"
    else
        echo -e "${RED}❌ Test failed${NC}"
    fi
    
    # Show result if exists
    if [ -f /tmp/flow_result.json ]; then
        echo "Result:"
        python -c "import json; print(json.dumps(json.load(open('/tmp/flow_result.json')), indent=2)[:500])"
        rm -f /tmp/flow_result.json
    fi
}

# Run all tests
run_test "real_test_basic.py"
run_test "real_test_gpu.py"
run_test "real_test_complex.py"
run_test "real_test_all_params.py"
run_test "real_test_error.py"

echo ""
echo "=========================================="
echo "✅ All tests completed!"
