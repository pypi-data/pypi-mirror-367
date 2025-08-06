"""
Main ftools commands implementation.

This module provides Python implementations of key Stata ftools commands:
- fegen: Fast generate (create group variables)
- flevelsof: Fast levels (extract unique values)
- fisid: Fast isid (check if variables uniquely identify observations)
- fsort: Fast sort using factor-based sorting
- join_factors: Join multiple factors efficiently
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional, Tuple, Any

try:
    from .factor import Factor
except ImportError:
    from factor import Factor


def fegen(
    data: pd.DataFrame,
    group_vars: Union[str, List[str]],
    function: str = "group",
    output_name: Optional[str] = None,
    replace: bool = False,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Fast generate - create group variables efficiently.
    
    Equivalent to Stata's "fegen newvar = group(varlist)".
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe
    group_vars : str or list of str
        Variables to create groups from
    function : str, default "group"
        Function to apply ("group" is primary, others may be added)
    output_name : str, optional
        Name for output variable. If None, uses "_group"
    replace : bool, default False
        Whether to replace existing column
    verbose : bool, default False
        Print debug information
        
    Returns
    -------
    pd.DataFrame
        DataFrame with new group variable added
        
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'firm': ['A', 'B', 'A', 'B', 'A'],
    ...     'year': [2020, 2020, 2021, 2021, 2020]
    ... })
    >>> result = fegen(df, ['firm', 'year'], output_name='group_id')
    """
    if isinstance(group_vars, str):
        group_vars = [group_vars]
    
    # Validate inputs
    for var in group_vars:
        if var not in data.columns:
            raise ValueError(f"Variable '{var}' not found in data")
    
    if output_name is None:
        output_name = "_group"
    
    if output_name in data.columns and not replace:
        raise ValueError(f"Variable '{output_name}' already exists. Use replace=True to overwrite.")
    
    # Create factor for group generation
    if len(group_vars) == 1:
        group_data = data[group_vars[0]]
    else:
        group_data = data[group_vars]
    
    factor = Factor(group_data, verbose=verbose)
    
    # Apply function (currently only 'group' supported)
    if function == "group":
        result_data = data.copy()
        result_data[output_name] = factor.levels
        
        if verbose:
            print(f"Created {factor.num_levels} groups from {len(group_vars)} variables")
        
        return result_data
    else:
        raise ValueError(f"Function '{function}' not supported yet")


def flevelsof(
    data: pd.DataFrame,
    variables: Union[str, List[str]],
    clean: bool = True,
    local_name: Optional[str] = None,
    missing: bool = False,
    separate: str = " ",
    verbose: bool = False
) -> Union[List, str]:
    """
    Fast levels - extract unique levels of variables.
    
    Equivalent to Stata's "flevelsof varlist".
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe
    variables : str or list of str
        Variables to extract levels from
    clean : bool, default True
        Remove extra spaces and format nicely
    local_name : str, optional
        Name for storing result (for compatibility - returns result anyway)
    missing : bool, default False
        Include missing values in results
    separate : str, default " "
        Separator for joining multiple values
    verbose : bool, default False
        Print debug information
        
    Returns
    -------
    List or str
        Unique levels, formatted according to options
        
    Examples
    --------
    >>> df = pd.DataFrame({'group': ['A', 'B', 'A', 'C', 'B']})
    >>> levels = flevelsof(df, 'group')
    >>> print(levels)  # ['A', 'B', 'C']
    """
    if isinstance(variables, str):
        variables = [variables]
    
    # Validate inputs
    for var in variables:
        if var not in data.columns:
            raise ValueError(f"Variable '{var}' not found in data")
    
    # Create factor to get unique levels efficiently
    if len(variables) == 1:
        var_data = data[variables[0]]
        if not missing:
            var_data = var_data.dropna()
    else:
        var_data = data[variables]
        if not missing:
            var_data = var_data.dropna()
    
    if len(var_data) == 0:
        return []
    
    factor = Factor(var_data, verbose=verbose)
    levels = factor.levels_of()
    
    # Format results
    if len(variables) == 1:
        # Single variable - return sorted unique values
        if isinstance(levels[0], (int, float)):
            result = sorted([x for x in levels if not (pd.isna(x) and not missing)])
        else:
            result = sorted([str(x) for x in levels if not (pd.isna(x) and not missing)])
        
        if clean and len(result) > 0:
            if isinstance(result[0], str):
                result = [x.strip() for x in result]
        
        if verbose:
            print(f"Found {len(result)} unique levels in {variables[0]}")
        
        return result
    else:
        # Multiple variables - return formatted strings
        result_strings = []
        for level_tuple in levels:
            if isinstance(level_tuple, tuple):
                level_str = separate.join([str(x) for x in level_tuple])
            else:
                level_str = str(level_tuple)
            
            if clean:
                level_str = level_str.strip()
            
            result_strings.append(level_str)
        
        if verbose:
            print(f"Found {len(result_strings)} unique combinations of {variables}")
        
        return result_strings


def fisid(
    data: pd.DataFrame,
    variables: Union[str, List[str]],
    sort: bool = False,
    missing_ok: bool = False,
    verbose: bool = False
) -> bool:
    """
    Fast isid - check if variables uniquely identify observations.
    
    Equivalent to Stata's "isid varlist".
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe
    variables : str or list of str
        Variables to check for uniqueness
    sort : bool, default False
        Sort data by variables first (for compatibility)
    missing_ok : bool, default False
        Allow missing values in ID variables
    verbose : bool, default False
        Print debug information
        
    Returns
    -------
    bool
        True if variables uniquely identify observations, False otherwise
        
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'id': [1, 2, 3, 4],
    ...     'group': ['A', 'A', 'B', 'B']
    ... })
    >>> fisid(df, 'id')  # True
    >>> fisid(df, 'group')  # False
    """
    if isinstance(variables, str):
        variables = [variables]
    
    # Validate inputs
    for var in variables:
        if var not in data.columns:
            raise ValueError(f"Variable '{var}' not found in data")
    
    # Check for missing values if not allowed
    if not missing_ok:
        subset_data = data[variables]
        if subset_data.isna().any().any():
            if verbose:
                print("Missing values found in ID variables")
            return False
    
    # Use Factor to efficiently check uniqueness
    if len(variables) == 1:
        var_data = data[variables[0]]
    else:
        var_data = data[variables]
    
    factor = Factor(var_data, verbose=verbose)
    
    # Check if it's a unique identifier (all groups have size 1)
    is_unique_id = factor.is_id()
    
    if verbose:
        if is_unique_id:
            print(f"Variables {variables} uniquely identify observations")
        else:
            print(f"Variables {variables} do NOT uniquely identify observations")
            print(f"Found {factor.num_levels} unique combinations for {factor.num_obs} observations")
            # Show some duplicates
            max_count = np.max(factor.counts)
            print(f"Largest group size: {max_count}")
    
    return is_unique_id


def fsort(
    data: pd.DataFrame,
    sort_vars: Union[str, List[str]],
    ascending: Union[bool, List[bool]] = True,
    stable: bool = True,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Fast sort using factor-based sorting.
    
    Equivalent to Stata's "fsort varlist" but with pandas-style options.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe to sort
    sort_vars : str or list of str
        Variables to sort by
    ascending : bool or list of bool, default True
        Sort ascending vs. descending
    stable : bool, default True
        Use stable sorting algorithm
    verbose : bool, default False
        Print debug information
        
    Returns
    -------
    pd.DataFrame
        Sorted dataframe
        
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'group': ['B', 'A', 'C', 'A'],
    ...     'value': [2, 1, 3, 4]
    ... })
    >>> sorted_df = fsort(df, ['group', 'value'])
    """
    if isinstance(sort_vars, str):
        sort_vars = [sort_vars]
    
    # Validate inputs
    for var in sort_vars:
        if var not in data.columns:
            raise ValueError(f"Variable '{var}' not found in data")
    
    # Handle ascending parameter
    if isinstance(ascending, bool):
        ascending = [ascending] * len(sort_vars)
    elif len(ascending) != len(sort_vars):
        raise ValueError("ascending must be bool or list of bools matching sort_vars length")
    
    # For now, use pandas sort_values as it's highly optimized
    # TODO: Implement factor-based sorting for large datasets
    result = data.sort_values(
        by=sort_vars, 
        ascending=ascending, 
        kind='mergesort' if stable else 'quicksort'
    ).reset_index(drop=True)
    
    if verbose:
        print(f"Sorted {len(data)} observations by {len(sort_vars)} variables")
    
    return result


def join_factors(*factors: Factor, verbose: bool = False) -> Factor:
    """
    Join multiple factors efficiently.
    
    Creates a new factor from the combination of multiple existing factors,
    similar to Stata's approach for multi-dimensional grouping.
    
    Parameters
    ----------
    *factors : Factor
        Factor objects to join
    verbose : bool, default False
        Print debug information
        
    Returns
    -------
    Factor
        New factor representing the combination
        
    Examples
    --------
    >>> f1 = Factor(['A', 'B', 'A', 'B'])
    >>> f2 = Factor([1, 1, 2, 2]) 
    >>> f_joined = join_factors(f1, f2)
    """
    if len(factors) == 0:
        raise ValueError("At least one factor required")
    
    if len(factors) == 1:
        return factors[0]
    
    # Check all factors have same number of observations
    num_obs = factors[0].num_obs
    for i, factor in enumerate(factors):
        if factor.num_obs != num_obs:
            raise ValueError(f"Factor {i} has {factor.num_obs} obs, expected {num_obs}")
    
    # Create combined data matrix
    combined_data = []
    
    for factor in factors:
        if factor.save_keys and factor.keys is not None:
            # Use the actual keys if available
            if factor.num_vars == 1:
                factor_data = factor.keys[factor.levels - 1]  # Convert to 0-indexed
            else:
                # Multi-variate factor
                factor_data = factor.keys[factor.levels - 1]  # This will be 2D
        else:
            # Use level numbers if keys not available
            factor_data = factor.levels
            
        combined_data.append(factor_data)
    
    # Stack the data appropriately
    if len(combined_data) == 2:
        # Simple case: two factors
        data1, data2 = combined_data
        if data1.ndim == 1 and data2.ndim == 1:
            combined_matrix = np.column_stack([data1, data2])
        else:
            # Handle more complex cases
            if data1.ndim == 1:
                data1 = data1.reshape(-1, 1)
            if data2.ndim == 1:
                data2 = data2.reshape(-1, 1)
            combined_matrix = np.column_stack([data1, data2])
    else:
        # Multiple factors - flatten and combine
        combined_list = []
        for data in combined_data:
            if data.ndim == 1:
                combined_list.append(data.reshape(-1, 1))
            else:
                combined_list.append(data)
        combined_matrix = np.column_stack(combined_list)
    
    # Create new factor from combined data
    result_factor = Factor(combined_matrix, verbose=verbose)
    
    if verbose:
        print(f"Joined {len(factors)} factors: {[f.num_levels for f in factors]} -> {result_factor.num_levels} levels")
    
    return result_factor


def fcount(
    data: pd.DataFrame,
    count_vars: Union[str, List[str]],
    output_name: str = "_count",
    by: Optional[Union[str, List[str]]] = None,
    replace: bool = False,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Fast count observations by groups.
    
    Similar to Stata's "bysort: gen _count = _N" but more flexible.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe
    count_vars : str or list of str
        Variables that define what to count (usually same as by)
    output_name : str, default "_count"
        Name for output count variable
    by : str or list of str, optional
        Grouping variables (if different from count_vars)
    replace : bool, default False
        Whether to replace existing column
    verbose : bool, default False
        Print debug information
        
    Returns
    -------
    pd.DataFrame
        DataFrame with count variable added
    """
    if by is None:
        by = count_vars
    
    if isinstance(by, str):
        by = [by]
    
    # Use fcollapse for the actual counting
    from .fcollapse import fcollapse
    
    # Create a temporary count column
    data_with_temp = data.copy()
    data_with_temp['_temp_count'] = 1
    
    # Collapse to get counts
    counts_df = fcollapse(
        data_with_temp, 
        stats={'count': ('count', '_temp_count')}, 
        by=by,
        verbose=verbose
    )
    
    # Rename the count column
    counts_df = counts_df.rename(columns={'count': output_name})
    
    # Ensure consistent data types before merging
    for col in by:
        if col in counts_df.columns:
            # Match the data type from original data
            original_dtype = data[col].dtype
            if counts_df[col].dtype != original_dtype:
                try:
                    counts_df[col] = counts_df[col].astype(original_dtype)
                except (ValueError, TypeError):
                    # If conversion fails, convert both to string
                    data_temp = data.copy()
                    data_temp[col] = data_temp[col].astype(str)
                    counts_df[col] = counts_df[col].astype(str)
                    result = data_temp.merge(counts_df, on=by, how='left')
                    # Fix output column existence check
                    if output_name in data.columns and not replace:
                        result = result.drop(columns=[output_name])
                        raise ValueError(f"Variable '{output_name}' already exists. Use replace=True to overwrite.")
                    return result
    
    # Merge back to original data
    result = data.merge(counts_df, on=by, how='left')
    
    if output_name in data.columns and not replace:
        # Remove the merged column and raise error
        result = result.drop(columns=[output_name])
        raise ValueError(f"Variable '{output_name}' already exists. Use replace=True to overwrite.")
    
    if verbose:
        unique_counts = result[output_name].value_counts().sort_index()
        print(f"Count distribution: {dict(unique_counts)}")
    
    return result