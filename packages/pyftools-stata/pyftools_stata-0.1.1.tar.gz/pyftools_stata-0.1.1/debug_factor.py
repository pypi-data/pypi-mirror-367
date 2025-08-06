#!/usr/bin/env python3
"""Debug Factor aggregation issue."""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyftools'))

from factor import Factor

def debug_aggregation():
    """Debug the aggregation issue step by step."""
    
    # Create simple test case
    groups = [1, 2, 1, 3, 2, 3, 1]
    values = [10, 20, 15, 30, 25, 35, 5]
    
    print(f"Groups: {groups}")
    print(f"Values: {values}")
    
    f = Factor(groups, verbose=True)
    print(f"\\nFactor levels: {f.levels}")
    print(f"Factor counts: {f.counts}")
    
    # Debug panelsetup
    f.panelsetup()
    print(f"\\nPanel setup completed")
    print(f"Info starts: {f.info.starts}")
    print(f"Info ends: {f.info.ends}")
    
    # Debug sort
    values_arr = np.array(values)
    sorted_values = f.sort(values_arr)
    print(f"\\nOriginal values: {values_arr}")
    print(f"Sorted values: {sorted_values}")
    print(f"Permutation p: {f.p}")
    
    # Debug panel operations manually
    print("\\nManual panel operations:")
    for i in range(f.num_levels):
        start = f.info.starts[i] 
        end = f.info.ends[i] + 1
        print(f"Level {i+1}: start={start}, end={end-1}, slice={sorted_values[start:end]}")
    
    # Try aggregation
    try:
        result = f.collapse(values, method='sum')
        print(f"\\nSum result: {result}")
    except Exception as e:
        print(f"\\nSum error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_aggregation()