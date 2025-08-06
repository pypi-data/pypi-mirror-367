#!/usr/bin/env python3
"""
Comprehensive test script for all ftools commands.
"""

import numpy as np
import pandas as pd
import sys
import os

# Add pyftools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyftools'))

import pyftools as ft

def create_test_data():
    """Create comprehensive test dataset."""
    np.random.seed(42)
    n = 100
    
    data = pd.DataFrame({
        'firm': np.random.choice(['Apple', 'Google', 'Microsoft', 'Amazon'], n),
        'year': np.random.choice([2020, 2021, 2022], n),
        'quarter': np.random.choice([1, 2, 3, 4], n),
        'region': np.random.choice(['US', 'EU', 'Asia'], n),
        'revenue': np.random.lognormal(10, 0.5, n),
        'employees': np.random.poisson(1000, n),
        'id': range(1, n+1),
        'duplicate_id': np.random.choice(range(1, n//2), n)  # Has duplicates
    })
    
    # Add some missing values
    data.loc[np.random.choice(n, 5, replace=False), 'revenue'] = np.nan
    
    return data

def test_fegen():
    """Test fegen functionality."""
    print("=== Testing fegen (Fast Generate) ===")
    
    data = create_test_data()
    print(f"Original data shape: {data.shape}")
    
    # Test 1: Single variable grouping
    result1 = ft.fegen(data, 'firm', output_name='firm_group', verbose=True)
    print(f"\\n1. Firm groups:")
    print(result1[['firm', 'firm_group']].drop_duplicates().sort_values('firm_group'))
    
    # Test 2: Multi-variable grouping
    result2 = ft.fegen(data, ['firm', 'year'], output_name='firm_year_group', verbose=True)
    print(f"\\n2. Firm-year groups:")
    print(result2[['firm', 'year', 'firm_year_group']].drop_duplicates().sort_values('firm_year_group').head(10))
    
    # Test 3: Complex grouping
    result3 = ft.fegen(data, ['firm', 'year', 'quarter'], output_name='complex_group', verbose=True)
    print(f"\\n3. Complex groups - unique count: {result3['complex_group'].nunique()}")
    
    return result1, result2, result3

def test_flevelsof():
    """Test flevelsof functionality."""
    print("\\n=== Testing flevelsof (Fast Levels) ===")
    
    data = create_test_data()
    
    # Test 1: Single variable
    levels1 = ft.flevelsof(data, 'firm', verbose=True)
    print(f"\\n1. Firm levels: {levels1}")
    
    # Test 2: Numeric variable
    levels2 = ft.flevelsof(data, 'year', verbose=True)
    print(f"\\n2. Year levels: {levels2}")
    
    # Test 3: Multiple variables
    levels3 = ft.flevelsof(data, ['firm', 'year'], verbose=True)
    print(f"\\n3. Firm-year combinations (first 5): {levels3[:5]}")
    
    # Test 4: With missing values
    levels4 = ft.flevelsof(data, 'revenue', missing=True, verbose=True)
    print(f"\\n4. Revenue levels (with missing): {len(levels4)} unique values")
    
    levels5 = ft.flevelsof(data, 'revenue', missing=False, verbose=True)  
    print(f"\\n5. Revenue levels (no missing): {len(levels5)} unique values")
    
    return levels1, levels2, levels3, levels4, levels5

def test_fisid():
    """Test fisid functionality."""
    print("\\n=== Testing fisid (Fast IsID) ===")
    
    data = create_test_data()
    
    # Test 1: Unique ID (should be True)
    is_id1 = ft.fisid(data, 'id', verbose=True)
    print(f"\\n1. Is 'id' a unique identifier? {is_id1}")
    
    # Test 2: Non-unique variable (should be False)
    is_id2 = ft.fisid(data, 'firm', verbose=True)
    print(f"\\n2. Is 'firm' a unique identifier? {is_id2}")
    
    # Test 3: Duplicate ID (should be False)
    is_id3 = ft.fisid(data, 'duplicate_id', verbose=True)
    print(f"\\n3. Is 'duplicate_id' a unique identifier? {is_id3}")
    
    # Test 4: Multi-variable ID
    is_id4 = ft.fisid(data, ['firm', 'year', 'quarter'], verbose=True)
    print(f"\\n4. Is ['firm', 'year', 'quarter'] a unique identifier? {is_id4}")
    
    # Test 5: Complete multi-variable ID
    is_id5 = ft.fisid(data, ['firm', 'year', 'quarter', 'region'], verbose=True)
    print(f"\\n5. Is ['firm', 'year', 'quarter', 'region'] a unique identifier? {is_id5}")
    
    return is_id1, is_id2, is_id3, is_id4, is_id5

def test_fsort():
    """Test fsort functionality."""
    print("\\n=== Testing fsort (Fast Sort) ===")
    
    data = create_test_data()
    print(f"Original data shape: {data.shape}")
    
    # Test 1: Single variable sort
    sorted1 = ft.fsort(data, 'firm', verbose=True)
    print(f"\\n1. Sorted by firm (first 5):")
    print(sorted1[['firm', 'year', 'revenue']].head())
    
    # Test 2: Multi-variable sort
    sorted2 = ft.fsort(data, ['firm', 'year'], verbose=True)
    print(f"\\n2. Sorted by firm and year (first 8):")
    print(sorted2[['firm', 'year', 'quarter', 'revenue']].head(8))
    
    # Test 3: Mixed ascending/descending
    sorted3 = ft.fsort(data, ['firm', 'revenue'], ascending=[True, False], verbose=True)
    print(f"\\n3. Sorted by firm (asc) and revenue (desc) (first 5):")
    print(sorted3[['firm', 'revenue']].head())
    
    return sorted1, sorted2, sorted3

def test_join_factors():
    """Test join_factors functionality."""
    print("\\n=== Testing join_factors ===")
    
    data = create_test_data()
    
    # Create individual factors
    f1 = ft.Factor(data['firm'], verbose=True)
    f2 = ft.Factor(data['year'], verbose=True)
    f3 = ft.Factor(data['quarter'], verbose=True)
    
    print(f"\\nOriginal factors:")
    print(f"F1 (firm): {f1.num_levels} levels")
    print(f"F2 (year): {f2.num_levels} levels") 
    print(f"F3 (quarter): {f3.num_levels} levels")
    
    # Test 1: Join two factors
    f_joined2 = ft.join_factors(f1, f2, verbose=True)
    print(f"\\n1. Joined F1+F2: {f_joined2.num_levels} levels")
    
    # Test 2: Join three factors
    f_joined3 = ft.join_factors(f1, f2, f3, verbose=True)
    print(f"\\n2. Joined F1+F2+F3: {f_joined3.num_levels} levels")
    
    # Test 3: Compare with direct multi-variable factor
    f_direct = ft.Factor(data[['firm', 'year', 'quarter']], verbose=True)
    print(f"\\n3. Direct multi-variable factor: {f_direct.num_levels} levels")
    
    print(f"\\nJoined vs Direct results match: {f_joined3.equals(f_direct)}")
    
    return f_joined2, f_joined3, f_direct

def test_fcount():
    """Test fcount functionality."""
    print("\\n=== Testing fcount ===")
    
    data = create_test_data()
    
    # Test 1: Count by single variable
    result1 = ft.fcount(data, 'firm', output_name='firm_count', verbose=True)
    print(f"\\n1. Count by firm:")
    print(result1[['firm', 'firm_count']].drop_duplicates().sort_values('firm'))
    
    # Test 2: Count by multiple variables
    result2 = ft.fcount(data, ['firm', 'year'], output_name='firm_year_count', verbose=True)
    print(f"\\n2. Count by firm-year (first 10):")
    print(result2[['firm', 'year', 'firm_year_count']].drop_duplicates().sort_values(['firm', 'year']).head(10))
    
    return result1, result2

def test_comprehensive_workflow():
    """Test a comprehensive workflow using multiple ftools."""
    print("\\n=== Comprehensive Workflow Test ===")
    
    data = create_test_data()
    print(f"Starting with {len(data)} observations")
    
    # Step 1: Create group identifiers
    data = ft.fegen(data, ['firm', 'year'], output_name='firm_year_id', verbose=True)
    
    # Step 2: Check if our new ID is unique
    is_unique = ft.fisid(data, 'firm_year_id', verbose=True)
    print(f"\\nNew ID is unique: {is_unique}")
    
    # Step 3: Get levels of our grouping
    levels = ft.flevelsof(data, ['firm', 'year'], verbose=True)
    print(f"\\nFound {len(levels)} unique firm-year combinations")
    
    # Step 4: Add count information
    data = ft.fcount(data, ['firm', 'year'], output_name='obs_per_group', verbose=True)
    
    # Step 5: Collapse to firm-year level
    collapsed = ft.fcollapse(
        data, 
        stats={'mean': 'revenue', 'sum': 'employees', 'count': 'id'}, 
        by=['firm', 'year'],
        freq=True,
        verbose=True
    )
    
    # Step 6: Sort final results
    final = ft.fsort(collapsed, ['firm', 'year'], verbose=True)
    
    print(f"\\nFinal result (first 10 rows):")
    print(final.head(10))
    
    print(f"\\nWorkflow completed: {len(data)} -> {len(final)} observations")
    
    return data, final

def benchmark_performance():
    """Benchmark ftools performance against pandas."""
    print("\\n=== Performance Benchmark ===")
    
    # Create larger dataset
    np.random.seed(42)
    n = 10000
    
    large_data = pd.DataFrame({
        'group1': np.random.choice(['A', 'B', 'C', 'D', 'E'], n),
        'group2': np.random.choice(range(1, 21), n),
        'group3': np.random.choice(['X', 'Y', 'Z'], n),
        'value1': np.random.randn(n),
        'value2': np.random.randn(n),
        'value3': np.random.randint(1, 100, n)
    })
    
    print(f"Testing with {n:,} observations")
    
    # Test fcollapse vs pandas groupby
    import time
    
    # PyFtools fcollapse
    start_time = time.time()
    result_ft = ft.fcollapse(large_data, stats='mean', by=['group1', 'group2'])
    ft_time = time.time() - start_time
    
    # Pandas groupby
    start_time = time.time()
    numeric_cols = large_data.select_dtypes(include=[np.number]).columns
    agg_cols = [col for col in numeric_cols if col not in ['group1', 'group2']]
    result_pd = large_data.groupby(['group1', 'group2'])[agg_cols].mean().reset_index()
    pd_time = time.time() - start_time
    
    print(f"\\nCollapse performance:")
    print(f"  PyFtools: {ft_time:.4f}s")
    print(f"  Pandas:   {pd_time:.4f}s")
    print(f"  Ratio:    {pd_time/ft_time:.2f}x")
    
    # Test fisid vs pandas
    start_time = time.time()
    is_id_ft = ft.fisid(large_data, ['group1', 'group2', 'group3'])
    ft_id_time = time.time() - start_time
    
    start_time = time.time()
    is_id_pd = len(large_data) == len(large_data[['group1', 'group2', 'group3']].drop_duplicates())
    pd_id_time = time.time() - start_time
    
    print(f"\\nUnique ID check performance:")
    print(f"  PyFtools: {ft_id_time:.4f}s (result: {is_id_ft})")
    print(f"  Pandas:   {pd_id_time:.4f}s (result: {is_id_pd})")
    print(f"  Ratio:    {pd_id_time/ft_id_time:.2f}x")

def main():
    """Run all tests."""
    print("PyFtools Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        test_fegen()
        test_flevelsof()
        test_fisid() 
        test_fsort()
        test_join_factors()
        test_fcount()
        test_comprehensive_workflow()
        benchmark_performance()
        
        print("\\n" + "=" * 60)
        print("All ftools tests completed successfully! ✅")
        print("\\nPyFtools now provides:")
        print("- ✅ Factor: Efficient categorical variable handling")
        print("- ✅ fcollapse: Fast aggregation operations") 
        print("- ✅ fegen: Fast group generation")
        print("- ✅ flevelsof: Extract unique levels")
        print("- ✅ fisid: Check unique identifiers")
        print("- ✅ fsort: Fast sorting (pandas-based)")
        print("- ✅ join_factors: Efficient factor joining")
        print("- ✅ fcount: Count observations by groups")
        
    except Exception as e:
        print(f"\\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())