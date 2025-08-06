#!/usr/bin/env python3
"""
Test script for the enhanced Factor class.
"""

import numpy as np
import pandas as pd
import sys
import os

# Add pyftools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyftools'))

from factor import Factor

def test_basic_functionality():
    """Test basic Factor creation and functionality."""
    print("=== Testing Basic Functionality ===")
    
    # Test 1: Simple integer data
    data = [1, 2, 1, 3, 2, 3, 1]
    f = Factor(data, verbose=True)
    print(f"Factor: {f}")
    f.summary()
    
    # Test 2: String data
    print("\n--- String Data Test ---")
    data_str = ['A', 'B', 'A', 'C', 'B', 'C', 'A']
    f_str = Factor(data_str, verbose=True)
    print(f"String Factor: {f_str}")
    
    # Test 3: Pandas Series
    print("\n--- Pandas Series Test ---")
    s = pd.Series([10, 20, 10, 30, 20])
    f_pd = Factor(s, verbose=True)
    print(f"Pandas Factor: {f_pd}")
    
    return f, f_str, f_pd

def test_hashing_methods():
    """Test different hashing methods."""
    print("\n=== Testing Hashing Methods ===")
    
    # Integer data that should use hash0
    int_data = np.array([1, 5, 1, 3, 5, 3, 7])
    
    # Force hash0
    f_hash0 = Factor(int_data, method="hash0", verbose=True)
    print(f"Hash0: {f_hash0}")
    
    # Force hash1
    f_hash1 = Factor(int_data, method="hash1", verbose=True)
    print(f"Hash1: {f_hash1}")
    
    # Auto selection
    f_auto = Factor(int_data, method="auto", verbose=True)
    print(f"Auto: {f_auto}")
    
    return f_hash0, f_hash1, f_auto

def test_multivariate():
    """Test multi-variable factors."""
    print("\n=== Testing Multivariate Factors ===")
    
    # Create multi-column data
    data = np.array([
        [1, 'A'],
        [2, 'B'],
        [1, 'A'],
        [3, 'C'],
        [2, 'B'],
        [1, 'B']
    ])
    
    f_multi = Factor(data, verbose=True)
    print(f"Multivariate Factor: {f_multi}")
    f_multi.summary()
    
    return f_multi

def test_aggregation():
    """Test aggregation operations."""
    print("\n=== Testing Aggregation Operations ===")
    
    # Create factor
    groups = [1, 2, 1, 3, 2, 3, 1]
    values = [10, 20, 15, 30, 25, 35, 5]
    
    f = Factor(groups, verbose=True)
    
    # Test different aggregation methods
    methods = ['sum', 'mean', 'count', 'min', 'max', 'first', 'last']
    
    print("\\nAggregation Results:")
    for method in methods:
        try:
            result = f.collapse(values, method=method)
            print(f"{method:>8}: {result}")
        except Exception as e:
            print(f"{method:>8}: Error - {e}")
    
    return f

def test_sorting_operations():
    """Test sorting and permutation operations."""
    print("\n=== Testing Sorting Operations ===")
    
    groups = [3, 1, 2, 1, 3, 2]
    values = [30, 10, 20, 15, 35, 25]
    
    f = Factor(groups, verbose=True)
    values_arr = np.array(values)
    
    print(f"Original values: {values}")
    print(f"Levels: {f.levels}")
    
    # Test sorting
    sorted_values = f.sort(values_arr)
    print(f"Sorted values: {sorted_values}")
    
    # Test inverse sorting
    restored_values = f.invsort(sorted_values)
    print(f"Restored values: {restored_values}")
    print(f"Match original: {np.array_equal(values_arr, restored_values)}")
    
    return f

def test_utility_functions():
    """Test utility functions."""
    print("\n=== Testing Utility Functions ===")
    
    # Create factors
    f1 = Factor([1, 1, 2, 2, 3])
    f2 = Factor([1, 1, 1, 2, 2])
    f3 = Factor([1, 2, 3, 4, 5])  # Unique ID
    
    print(f"F1 levels: {f1.levels_of()}")
    print(f"F1 is ID: {f1.is_id()}")
    print(f"F3 is ID: {f3.is_id()}")
    print(f"F1 nested in F2: {f1.nested_within(f2)}")
    print(f"F2 nested in F1: {f2.nested_within(f1)}")
    
    return f1, f2, f3

def main():
    """Run all tests."""
    print("PyFtools Enhanced Factor Class Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        test_basic_functionality()
        test_hashing_methods()
        test_multivariate()
        test_aggregation()
        test_sorting_operations()
        test_utility_functions()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())