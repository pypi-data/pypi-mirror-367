#!/usr/bin/env python3

# Test to reproduce the bug in make_partial_function
import sys
sys.path.insert(0, 'src')

from mcp_server_qdrant.common.func_tools import make_partial_function

def test_function(a, b, c):
    return f"a={a}, b={b}, c={c}"

try:
    # This should fail with NameError: name 'remaining_params' is not defined
    partial_func = make_partial_function(test_function, {"c": "fixed"})
    print("SUCCESS: Function created successfully")
    result = partial_func("value_a", "value_b")
    print(f"Result: {result}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")