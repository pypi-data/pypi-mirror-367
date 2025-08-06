#!/usr/bin/env python3
"""
Test script for fcollapse functionality.
"""

import numpy as np
import pandas as pd
import sys
import os

# Add pyftools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyftools'))

import pyftools as ft
from pyftools.fcollapse import fcollapse, fsum, fmean, fcount

def create_test_data():
    """Create test dataset similar to common econometric data."""
    np.random.seed(42)
    n = 1000
    
    data = pd.DataFrame({
        'firm_id': np.random.choice(['A', 'B', 'C', 'D', 'E'], n),
        'year': np.random.choice([2018, 2019, 2020, 2021, 2022], n),
        'industry': np.random.choice(['Tech', 'Finance', 'Manufacturing'], n),
        'revenue': np.random.lognormal(10, 1, n),
        'employees': np.random.poisson(50, n),
        'profit': np.random.normal(1000000, 500000, n),
        'weight': np.random.uniform(0.5, 2.0, n)
    })
    
    # Add some missing values
    data.loc[np.random.choice(n, 50, replace=False), 'profit'] = np.nan
    data.loc[np.random.choice(n, 30, replace=False), 'employees'] = np.nan
    
    return data

def test_basic_collapse():
    """Test basic collapse operations."""
    print("=== Testing Basic Collapse Operations ===")
    
    data = create_test_data()
    print(f"Original data shape: {data.shape}")
    
    # Test 1: Collapse entire dataset
    print("\\n1. Collapse entire dataset (sum):")
    result1 = fcollapse(data, stats='sum', verbose=True)
    print(result1.head())
    
    # Test 2: Collapse by single group
    print("\\n2. Collapse by firm_id:")
    result2 = fcollapse(data, stats='sum', by='firm_id', verbose=True)
    print(result2.head())
    
    # Test 3: Collapse by multiple groups
    print("\\n3. Collapse by firm_id and year:")
    result3 = fcollapse(data, stats='mean', by=['firm_id', 'year'], verbose=True)
    print(result3.head())
    
    return data, result1, result2, result3

def test_multiple_stats():
    """Test multiple statistics."""
    print("\\n=== Testing Multiple Statistics ===")
    
    data = create_test_data()
    
    # Test different ways to specify multiple stats
    print("\\n1. Multiple stats as list:")
    result1 = fcollapse(data, stats=['sum', 'mean', 'count'], by='firm_id', verbose=True)
    print(result1.columns.tolist())
    print(result1.head(2))
    
    print("\\n2. Stats as dictionary:")
    stats_dict = {
        'total_revenue': ('sum', 'revenue'),
        'avg_employees': ('mean', 'employees'),
        'max_profit': ('max', 'profit'),
        'min_profit': ('min', 'profit')
    }
    result2 = fcollapse(data, stats=stats_dict, by='industry', verbose=True)
    print(result2.head())
    
    return result1, result2

def test_weights_and_freq():
    """Test weighted aggregation and frequency."""
    print("\\n=== Testing Weights and Frequency ===")
    
    data = create_test_data()
    
    # Test weighted aggregation
    print("\\n1. Weighted mean:")
    result1 = fcollapse(data, stats='mean', by='industry', 
                       weights='weight', freq=True, verbose=True)
    print(result1.head())
    
    # Compare with unweighted
    print("\\n2. Unweighted mean for comparison:")
    result2 = fcollapse(data, stats='mean', by='industry', 
                       freq=True, verbose=True)
    print(result2.head())
    
    return result1, result2

def test_convenience_functions():
    """Test convenience functions."""
    print("\\n=== Testing Convenience Functions ===")
    
    data = create_test_data()
    
    # Test fsum, fmean, fcount
    print("\\n1. Using fsum:")
    result1 = fsum(data, by='firm_id', verbose=True)
    print(result1.head(3))
    
    print("\\n2. Using fmean:")
    result2 = fmean(data, by='industry', verbose=True)
    print(result2.head())
    
    print("\\n3. Using fcount:")
    result3 = fcount(data, by=['firm_id', 'year'], verbose=True)
    print(result3.head())
    
    return result1, result2, result3

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\\n=== Testing Edge Cases ===")
    
    data = create_test_data()
    
    # Test with missing values and cw option
    print("\\n1. Casewise deletion (cw=True):")
    result1 = fcollapse(data, stats='mean', by='firm_id', cw=True, verbose=True)
    print(f"Result shape: {result1.shape}")
    
    print("\\n2. Without casewise deletion:")
    result2 = fcollapse(data, stats='mean', by='firm_id', cw=False, verbose=True)
    print(f"Result shape: {result2.shape}")
    
    # Test error cases
    try:
        print("\\n3. Testing error: invalid column")
        fcollapse(data, stats='sum', by='nonexistent_col')
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    try:
        print("\\n4. Testing error: merge and append")
        fcollapse(data, stats='sum', by='firm_id', merge=True, append=True)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    return result1, result2

def compare_with_pandas():
    """Compare performance and results with pandas groupby."""
    print("\\n=== Comparing with Pandas Groupby ===")
    
    data = create_test_data()
    
    # PyFtools approach
    import time
    
    start_time = time.time()
    result_pyftools = fcollapse(data, stats='sum', by=['firm_id', 'year'])
    pyftools_time = time.time() - start_time
    
    # Pandas approach
    start_time = time.time()
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    # Exclude grouping columns from aggregation to avoid conflicts
    agg_cols = [col for col in numeric_cols if col not in ['firm_id', 'year']]
    result_pandas = data.groupby(['firm_id', 'year'])[agg_cols].sum().reset_index()
    pandas_time = time.time() - start_time
    
    print(f"PyFtools time: {pyftools_time:.4f}s")
    print(f"Pandas time: {pandas_time:.4f}s")
    print(f"Speed ratio: {pandas_time/pyftools_time:.2f}x")
    
    # Check results are similar (allowing for small numerical differences)
    print(f"\\nResult shapes - PyFtools: {result_pyftools.shape}, Pandas: {result_pandas.shape}")
    
    # Compare a few values
    print("\\nSample comparisons:")
    for col in ['revenue', 'employees', 'profit']:
        if col in result_pyftools.columns and col in result_pandas.columns:
            pf_val = result_pyftools[col].iloc[0]
            pd_val = result_pandas[col].iloc[0]
            print(f"{col}: PyFtools={pf_val:.2f}, Pandas={pd_val:.2f}")
    
    return result_pyftools, result_pandas

def main():
    """Run all fcollapse tests."""
    print("PyFtools fcollapse Test Suite")
    print("=" * 50)
    
    try:
        test_basic_collapse()
        test_multiple_stats()
        test_weights_and_freq()
        test_convenience_functions()
        test_edge_cases()
        compare_with_pandas()
        
        print("\\n" + "=" * 50)
        print("All fcollapse tests completed successfully!")
        
    except Exception as e:
        print(f"\\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())