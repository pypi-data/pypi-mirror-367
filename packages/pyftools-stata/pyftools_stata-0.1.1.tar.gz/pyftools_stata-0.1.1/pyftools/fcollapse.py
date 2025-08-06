"""
Fast collapse (fcollapse) implementation.

This module provides the fcollapse function that mimics Stata's fcollapse command,
offering fast aggregation operations on pandas DataFrames using the Factor class.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Dict, Optional, Any, Tuple
import warnings

try:
    from .factor import Factor
except ImportError:
    from factor import Factor


def fcollapse(
    data: pd.DataFrame,
    stats: Union[str, List[str], Dict[str, str]] = "sum",
    by: Optional[Union[str, List[str]]] = None,
    weights: Optional[str] = None,
    freq: bool = False,
    freq_name: str = "_freq",
    cw: bool = False,
    fast: bool = True,
    merge: bool = False,
    append: bool = False,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Fast collapse operation equivalent to Stata's fcollapse.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe to collapse
    stats : str, list, or dict, default "sum"
        Aggregation statistics to compute. Can be:
        - Single string: apply to all numeric columns
        - List of strings: apply all stats to all numeric columns
        - Dict: {stat: columns} or {new_name: (stat, column)}
    by : str or list of str, optional
        Grouping variables. If None, collapse entire dataset to single row.
    weights : str, optional
        Column name to use as weights for aggregation
    freq : bool, default False
        Add frequency count column
    freq_name : str, default "_freq"
        Name for frequency column
    cw : bool, default False
        Casewise deletion of missing values
    fast : bool, default True
        Use fast Factor-based implementation
    merge : bool, default False
        Merge results back to original data (like egen)
    append : bool, default False
        Append results to original data
    verbose : bool, default False
        Print debug information
        
    Returns
    -------
    pd.DataFrame
        Collapsed dataframe
        
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'group': ['A', 'B', 'A', 'B', 'A'],
    ...     'x': [1, 2, 3, 4, 5],
    ...     'y': [10, 20, 30, 40, 50]
    ... })
    >>> fcollapse(df, stats='sum', by='group')
    """
    if not fast:
        warnings.warn("Non-fast mode not yet implemented, using fast mode")
    
    # Validate inputs
    if merge and append:
        raise ValueError("Cannot specify both merge and append")
    
    # Handle empty by clause
    if by is None:
        # Collapse entire dataset to single observation
        result_df = _collapse_all(data, stats, weights, freq, freq_name, cw, verbose)
    else:
        # Group-wise collapse
        result_df = _collapse_by_groups(data, stats, by, weights, freq, freq_name, cw, verbose)
    
    # Handle merge/append options
    if merge:
        return _merge_results(data, result_df, by)
    elif append:
        return _append_results(data, result_df)
    else:
        return result_df


def _parse_stats_spec(stats: Union[str, List[str], Dict[str, Any]], 
                      data: pd.DataFrame) -> List[Tuple[str, str, str]]:
    """
    Parse statistics specification into list of (output_name, stat, column) tuples.
    
    Returns
    -------
    List of (output_name, stat_function, column_name) tuples
    """
    result = []
    
    if isinstance(stats, str):
        # Single stat applied to all numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            result.append((col, stats, col))
    
    elif isinstance(stats, list):
        # List of stats applied to all numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for stat in stats:
            for col in numeric_cols:
                output_name = f"{col}_{stat}" if len(stats) > 1 else col
                result.append((output_name, stat, col))
    
    elif isinstance(stats, dict):
        # Dictionary specification
        for key, value in stats.items():
            if isinstance(value, str):
                # {stat: column} format - apply stat to specific column
                result.append((key, key, value))
            elif isinstance(value, tuple) and len(value) == 2:
                # {output_name: (stat, column)} format
                stat, col = value
                result.append((key, stat, col))
            elif isinstance(value, list):
                # {stat: [columns]} format - apply stat to multiple columns
                for col in value:
                    output_name = f"{col}_{key}"
                    result.append((output_name, key, col))
            else:
                raise ValueError(f"Invalid stats specification for key {key}: {value}")
    
    else:
        raise ValueError(f"Invalid stats specification: {stats}")
    
    return result


def _collapse_all(data: pd.DataFrame, stats, weights, freq, freq_name, cw, verbose) -> pd.DataFrame:
    """Collapse entire dataframe to single row."""
    stats_specs = _parse_stats_spec(stats, data)
    
    # Create results dictionary
    results = {}
    
    # Handle weights
    weights_array = None
    if weights is not None:
        if weights not in data.columns:
            raise ValueError(f"Weight column '{weights}' not found in data")
        weights_array = data[weights].values
    
    # Apply each statistic
    for output_name, stat, col in stats_specs:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in data")
        
        values = data[col]
        
        # Handle missing values if cw=True
        if cw:
            if weights_array is not None:
                mask = ~(pd.isna(values) | pd.isna(weights_array))
                values = values[mask]
                weights_subset = weights_array[mask]
            else:
                values = values.dropna()
                weights_subset = None
        else:
            weights_subset = weights_array
        
        # Compute statistic
        result_value = _compute_statistic(values.values, stat, weights_subset)
        results[output_name] = result_value
    
    # Add frequency if requested
    if freq:
        if cw:
            # Count non-missing observations
            non_missing = ~data.select_dtypes(include=[np.number]).isna().any(axis=1)
            results[freq_name] = non_missing.sum()
        else:
            results[freq_name] = len(data)
    
    # Create result DataFrame
    result_df = pd.DataFrame([results])
    
    if verbose:
        print(f"Collapsed {len(data)} observations to 1 row")
    
    return result_df


def _collapse_by_groups(data: pd.DataFrame, stats, by, weights, freq, freq_name, cw, verbose) -> pd.DataFrame:
    """Collapse dataframe by groups using Factor class."""
    stats_specs = _parse_stats_spec(stats, data)
    
    # Validate by columns
    if isinstance(by, str):
        by = [by]
    
    for col in by:
        if col not in data.columns:
            raise ValueError(f"Grouping variable '{col}' not found in data")
    
    # Create factor for grouping variables
    if len(by) == 1:
        group_data = data[by[0]]
    else:
        group_data = data[by]
    
    factor = Factor(group_data, verbose=verbose)
    
    # Handle weights
    weights_array = None
    if weights is not None:
        if weights not in data.columns:
            raise ValueError(f"Weight column '{weights}' not found in data")
        weights_array = data[weights].values
    
    # Initialize results dictionary
    results = {}
    
    # Add group keys to results
    if factor.save_keys and factor.keys is not None:
        if factor.num_vars == 1:
            results[by[0]] = factor.keys
        else:
            # Multi-variable grouping
            for i, col in enumerate(by):
                if factor.keys.dtype == object:
                    # Object array contains tuples
                    results[col] = [key[i] for key in factor.keys]
                else:
                    results[col] = factor.keys[:, i]
    else:
        # Fallback: create group indices
        for i, col in enumerate(by):
            results[col] = np.arange(1, factor.num_levels + 1)
    
    # Apply each statistic using Factor operations
    for output_name, stat, col in stats_specs:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in data")
        
        values = data[col].values
        
        # Use Factor's collapse method for efficient aggregation
        result_values = factor.collapse(values, method=stat, weights=weights_array)
        results[output_name] = result_values
    
    # Add frequency if requested  
    if freq:
        results[freq_name] = factor.counts
    
    # Create result DataFrame
    result_df = pd.DataFrame(results)
    
    if verbose:
        print(f"Collapsed {len(data)} observations to {len(result_df)} groups")
    
    return result_df


def _compute_statistic(values: np.ndarray, stat: str, weights: Optional[np.ndarray] = None) -> float:
    """Compute a single statistic on values."""
    if len(values) == 0:
        return np.nan
    
    if stat == "sum":
        if weights is not None:
            return np.sum(values * weights)
        else:
            return np.sum(values)
    elif stat == "mean":
        if weights is not None:
            return np.average(values, weights=weights)
        else:
            return np.mean(values)
    elif stat == "count":
        if weights is not None:
            return np.sum(weights)
        else:
            return len(values)
    elif stat == "min":
        return np.min(values)
    elif stat == "max":
        return np.max(values)
    elif stat == "std":
        if weights is not None:
            return np.sqrt(np.average((values - np.average(values, weights=weights))**2, weights=weights))
        else:
            return np.std(values, ddof=1)  # Use sample standard deviation
    elif stat == "first":
        return values[0]
    elif stat == "last":
        return values[-1]
    elif stat in ["p25", "p50", "p75"]:
        # Percentiles
        percentile = float(stat[1:])
        return np.percentile(values, percentile)
    else:
        raise ValueError(f"Unknown statistic: {stat}")


def _merge_results(original: pd.DataFrame, results: pd.DataFrame, by: List[str]) -> pd.DataFrame:
    """Merge collapsed results back to original data (like egen)."""
    return original.merge(results, on=by, how='left')


def _append_results(original: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    """Append collapsed results to original data."""
    # Ensure compatible columns
    for col in results.columns:
        if col not in original.columns:
            original[col] = np.nan
    
    # Add missing columns to results with NaN
    for col in original.columns:
        if col not in results.columns:
            results[col] = np.nan
    
    # Reorder columns to match original
    results = results[original.columns]
    
    return pd.concat([original, results], ignore_index=True)


# Convenience functions for common operations
def fsum(data: pd.DataFrame, by: Optional[Union[str, List[str]]] = None, **kwargs) -> pd.DataFrame:
    """Convenience function for sum aggregation."""
    return fcollapse(data, stats="sum", by=by, **kwargs)


def fmean(data: pd.DataFrame, by: Optional[Union[str, List[str]]] = None, **kwargs) -> pd.DataFrame:
    """Convenience function for mean aggregation.""" 
    return fcollapse(data, stats="mean", by=by, **kwargs)


def fcount(data: pd.DataFrame, by: Optional[Union[str, List[str]]] = None, **kwargs) -> pd.DataFrame:
    """Convenience function for count aggregation."""
    return fcollapse(data, stats="count", by=by, **kwargs)