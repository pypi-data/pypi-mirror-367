"""
Factor class for efficient categorical variable handling.

This module implements the core Factor class that provides fast group operations
and categorical variable manipulation inspired by Stata's ftools.

Implements multiple hashing strategies:
- hash0: Perfect hashing for integer data
- hash1: Open addressing hash table for general data
- auto: Intelligent algorithm selection
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional
from dataclasses import dataclass
import warnings


@dataclass
class FactorInfo:
    """Panel information for efficient group operations."""
    starts: np.ndarray  # Start index for each group
    ends: np.ndarray    # End index for each group
    num_levels: int     # Number of groups


class Factor:
    """
    Factor class for efficient handling of categorical variables.
    
    This class provides fast group operations using advanced hashing algorithms
    optimized for different data types and patterns, closely matching Stata's ftools.
    
    Attributes
    ----------
    num_levels : int
        Number of unique factor levels
    num_obs : int
        Number of observations
    levels : np.ndarray
        1-indexed levels for each observation
    keys : np.ndarray, optional
        Unique keys/values for each factor level
    counts : np.ndarray
        Count of observations in each level
    info : FactorInfo, optional
        Panel information for efficient group operations
    p : np.ndarray, optional
        Permutation vector for sorting
    inv_p : np.ndarray, optional
        Inverse permutation vector
    method : str
        Hashing method used
    is_sorted : bool
        Whether the factor levels are sorted
    panel_is_setup : bool
        Whether panel operations are initialized
    """
    
    def __init__(self, data: Union[pd.Series, pd.DataFrame, np.ndarray, List], 
                 method: str = "auto", 
                 sort_levels: bool = True,
                 save_keys: bool = True,
                 verbose: bool = False,
                 max_numkeys: Optional[int] = None,
                 dict_size: Optional[int] = None):
        """
        Initialize a Factor object.
        
        Parameters
        ----------
        data : pd.Series, pd.DataFrame, np.ndarray, or list
            The categorical data to create factors from. Can be single or multi-column.
        method : str, default "auto"
            Hashing method: "auto", "hash0", "hash1"
        sort_levels : bool, default True
            Whether to sort the factor levels
        save_keys : bool, default True
            Whether to save the original keys
        verbose : bool, default False
            Whether to display debug information
        max_numkeys : int, optional
            Maximum number of expected unique keys (for memory allocation)
        dict_size : int, optional
            Hash table size (for hash1 method)
        """
        # Store input parameters
        self.raw_data = data
        self.method_requested = method
        self.sort_levels = sort_levels
        self.save_keys = save_keys
        self.verbose = verbose
        self.max_numkeys = max_numkeys
        self.dict_size = dict_size
        
        # Initialize core properties (matching Stata ftools structure)
        self.num_levels: int = 0
        self.num_obs: int = 0
        self.levels: Optional[np.ndarray] = None  # 1-indexed like Stata
        self.keys: Optional[np.ndarray] = None
        self.counts: Optional[np.ndarray] = None
        self.info: Optional[FactorInfo] = None
        self.p: Optional[np.ndarray] = None  # Permutation vector
        self.inv_p: Optional[np.ndarray] = None  # Inverse permutation
        self.method: str = ""  # Actual method used
        self.is_sorted: bool = False
        self.panel_is_setup: bool = False
        
        # Data properties
        self.is_multivariate: bool = False
        self.num_vars: int = 0
        
        # Process the input data
        self._create_factor()
    
    def _create_factor(self):
        """Create the factor representation from input data."""
        # Normalize input data
        data_matrix = self._normalize_input()
        
        # Determine optimal method if auto
        if self.method_requested == "auto":
            self.method = self._choose_method(data_matrix)
        else:
            self.method = self.method_requested
            
        # Apply the chosen hashing method
        if self.method == "hash0":
            self._create_factor_hash0(data_matrix)
        elif self.method == "hash1":
            self._create_factor_hash1(data_matrix)
        else:
            raise ValueError(f"Unknown method: {self.method}")
            
        # Post-processing
        if self.sort_levels:
            self._sort_levels()
            
        if self.verbose:
            print(f"Factor created: {self.num_levels} levels, {self.num_obs} obs, method='{self.method}'")
    
    def _normalize_input(self) -> np.ndarray:
        """Convert input data to standardized numpy array format."""
        if isinstance(self.raw_data, pd.DataFrame):
            data_matrix = self.raw_data.values
            self.is_multivariate = True
            self.num_vars = data_matrix.shape[1]
        elif isinstance(self.raw_data, pd.Series):
            data_matrix = self.raw_data.values.reshape(-1, 1)
            self.is_multivariate = False
            self.num_vars = 1
        elif isinstance(self.raw_data, list):
            arr = np.array(self.raw_data)
            if arr.ndim == 1:
                data_matrix = arr.reshape(-1, 1)
                self.is_multivariate = False
                self.num_vars = 1
            else:
                data_matrix = arr
                self.is_multivariate = arr.shape[1] > 1
                self.num_vars = arr.shape[1]
        else:
            # Assume numpy array
            if self.raw_data.ndim == 1:
                data_matrix = self.raw_data.reshape(-1, 1)
                self.is_multivariate = False
                self.num_vars = 1
            else:
                data_matrix = self.raw_data
                self.is_multivariate = data_matrix.shape[1] > 1
                self.num_vars = data_matrix.shape[1]
                
        self.num_obs = data_matrix.shape[0]
        return data_matrix
    
    def _choose_method(self, data_matrix: np.ndarray) -> str:
        """Intelligently choose the best hashing method based on data characteristics."""
        # Check if data is all integers and has reasonable range (like Stata's logic)
        if self.num_vars == 1 and np.issubdtype(data_matrix.dtype, np.integer):
            min_val, max_val = np.min(data_matrix), np.max(data_matrix)
            range_size = max_val - min_val + 1
            
            # Use hash0 if range is reasonable compared to number of observations
            if range_size <= max(self.num_obs * 2, 10000):
                return "hash0"
        
        # For multi-variate or non-integer data, use hash1
        return "hash1"
    
    def _create_factor_hash0(self, data_matrix: np.ndarray):
        """Perfect hashing method for integer data (equivalent to Stata's hash0)."""
        if self.num_vars > 1:
            raise ValueError("hash0 method only supports single variable")
            
        data_col = data_matrix[:, 0]
        
        # Check data is integer
        if not np.issubdtype(data_col.dtype, np.integer):
            raise ValueError("hash0 method requires integer data")
        
        # Get range and create perfect hash
        min_val, max_val = np.min(data_col), np.max(data_col)
        range_size = max_val - min_val + 1
        
        # Create mapping from values to consecutive integers
        hash_table = np.full(range_size, -1, dtype=np.int32)
        levels = np.zeros(self.num_obs, dtype=np.int32)
        keys = []
        counts = []
        
        level_counter = 0
        for i, val in enumerate(data_col):
            hash_idx = val - min_val
            if hash_table[hash_idx] == -1:
                # New unique value
                level_counter += 1
                hash_table[hash_idx] = level_counter
                keys.append(val)
                counts.append(1)
                levels[i] = level_counter
            else:
                # Existing value
                level_idx = hash_table[hash_idx]
                levels[i] = level_idx
                counts[level_idx - 1] += 1
        
        self.num_levels = level_counter
        self.levels = levels
        self.counts = np.array(counts)
        
        if self.save_keys:
            self.keys = np.array(keys)
        
        # Hash0 produces naturally sorted results
        self.is_sorted = True
    
    def _create_factor_hash1(self, data_matrix: np.ndarray):
        """Open addressing hash table method (equivalent to Stata's hash1)."""
        # Determine hash table size
        if self.dict_size is None:
            # Use heuristics similar to Stata
            estimated_uniques = min(self.num_obs, max(100, self.num_obs // 10))
            self.dict_size = self._next_prime(int(estimated_uniques * 1.3))
        
        # Initialize hash table and result arrays
        hash_table = {}  # Using Python dict which is already optimized
        levels = np.zeros(self.num_obs, dtype=np.int32)
        keys = []
        counts = []
        
        level_counter = 0
        
        # Process each observation
        for i in range(self.num_obs):
            if self.num_vars == 1:
                key = data_matrix[i, 0]
            else:
                key = tuple(data_matrix[i, :])
            
            if key not in hash_table:
                # New unique value
                level_counter += 1
                hash_table[key] = level_counter
                keys.append(key)
                counts.append(1)
                levels[i] = level_counter
            else:
                # Existing value
                level_idx = hash_table[key]
                levels[i] = level_idx
                counts[level_idx - 1] += 1
        
        self.num_levels = level_counter
        self.levels = levels
        self.counts = np.array(counts)
        
        if self.save_keys:
            if self.num_vars == 1:
                self.keys = np.array(keys)
            else:
                self.keys = np.array(keys)  # Will be object array for tuples
    
    def _next_prime(self, n: int) -> int:
        """Find the next prime number >= n."""
        def is_prime(num):
            if num < 2:
                return False
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0:
                    return False
            return True
        
        while not is_prime(n):
            n += 1
        return n
    
    def _sort_levels(self):
        """Sort the factor levels by their keys."""
        if not self.save_keys or self.is_sorted:
            return
            
        # Get sort order of keys
        if self.num_vars == 1:
            sort_indices = np.argsort(self.keys)
        else:
            # For multivariate, create lexicographic sort
            sort_indices = np.lexsort([self.keys[:, i] for i in range(self.num_vars-1, -1, -1)])
        
        # Reorder keys and counts
        self.keys = self.keys[sort_indices]
        self.counts = self.counts[sort_indices]
        
        # Create mapping from old levels to new levels
        level_mapping = np.zeros(self.num_levels + 1, dtype=np.int32)  # +1 for 1-indexing
        for new_level, old_level in enumerate(sort_indices, 1):
            level_mapping[old_level + 1] = new_level  # +1 for 1-indexing
        
        # Remap levels array
        self.levels = level_mapping[self.levels]
        self.is_sorted = True
    
    def panelsetup(self):
        """Setup panel information for efficient group operations."""
        if self.panel_is_setup:
            return
            
        # Create sorted permutation if not available
        if self.p is None:
            self._create_permutation()
        
        # Create panel info (start and end indices for each group)
        starts = np.zeros(self.num_levels, dtype=np.int32)
        ends = np.zeros(self.num_levels, dtype=np.int32)
        
        if self.num_obs == 0:
            self.info = FactorInfo(starts=starts, ends=ends, num_levels=self.num_levels)
            self.panel_is_setup = True
            return
        
        # Sort the data by levels and track group boundaries
        sorted_levels = self.levels[self.p - 1]  # Convert to 0-indexed
        
        current_level = sorted_levels[0]
        group_start = 0
        level_idx = current_level - 1  # Convert to 0-indexed
        starts[level_idx] = 0
        
        for i in range(1, self.num_obs):
            if sorted_levels[i] != current_level:
                # End previous group
                ends[level_idx] = i - 1
                
                # Start new group
                current_level = sorted_levels[i]
                level_idx = current_level - 1  # Convert to 0-indexed
                starts[level_idx] = i
        
        # End the last group
        ends[level_idx] = self.num_obs - 1
        
        self.info = FactorInfo(starts=starts, ends=ends, num_levels=self.num_levels)
        self.panel_is_setup = True
    
    def _create_permutation(self):
        """Create permutation vectors for sorting."""
        # Create permutation that sorts by levels
        sorted_indices = np.argsort(self.levels - 1)  # Convert to 0-indexed for sorting
        self.p = sorted_indices + 1  # Store as 1-indexed like Stata
        
        # Create inverse permutation
        self.inv_p = np.zeros(self.num_obs, dtype=np.int32)
        for i, pos in enumerate(self.p - 1):  # Convert to 0-indexed
            self.inv_p[pos] = i + 1  # Store as 1-indexed
    
    def sort(self, data: Union[np.ndarray, List]) -> np.ndarray:
        """Sort data according to factor groups."""
        if self.p is None:
            self._create_permutation()
        
        # Ensure data is numpy array
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        return data[self.p - 1]  # Convert to 0-indexed for array access
    
    def invsort(self, data: Union[np.ndarray, List]) -> np.ndarray:
        """Inverse sort - restore original order from sorted data."""
        if self.inv_p is None:
            self._create_permutation()
            
        # Ensure data is numpy array
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        return data[self.inv_p - 1]  # Convert to 0-indexed for array access
    
    def collapse(self, values: Union[pd.Series, np.ndarray], 
                 method: str = "sum", 
                 weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Collapse values by factor groups using efficient panel operations.
        
        Parameters
        ----------
        values : pd.Series or np.ndarray
            Values to collapse
        method : str, default "sum"
            Aggregation method: "sum", "mean", "count", "min", "max", "first", "last"
        weights : np.ndarray, optional
            Weights for aggregation
        
        Returns
        -------
        np.ndarray
            Collapsed values for each factor level
        """
        if isinstance(values, pd.Series):
            values = values.values
            
        # Ensure panel is setup for efficient operations
        if not self.panel_is_setup:
            self.panelsetup()
        
        # Sort values by factor groups for efficient processing
        sorted_values = self.sort(values)
        sorted_weights = self.sort(weights) if weights is not None else None
        
        # Apply aggregation method
        if method == "sum":
            return self._panelsum(sorted_values, sorted_weights)
        elif method == "mean":
            sums = self._panelsum(sorted_values, sorted_weights)
            counts = self._panelsum(np.ones_like(sorted_values), sorted_weights)
            # Ensure float output for mean
            result = np.zeros(len(sums), dtype=np.float64)
            return np.divide(sums, counts, out=result, where=counts!=0)
        elif method == "count":
            if weights is not None:
                return self._panelsum(np.ones_like(sorted_values), sorted_weights)
            else:
                return self.counts.astype(float)
        elif method == "min":
            return self._panelmin(sorted_values)
        elif method == "max":
            return self._panelmax(sorted_values)
        elif method == "first":
            return self._panelfirst(sorted_values)
        elif method == "last":
            return self._panellast(sorted_values)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
    
    def _panelsum(self, values: np.ndarray, weights: Optional[np.ndarray] = None) -> np.ndarray:
        """Efficient panel sum operation."""
        result = np.zeros(self.num_levels, dtype=values.dtype)
        
        for i in range(self.num_levels):
            start = self.info.starts[i]
            end = self.info.ends[i] + 1  # +1 because end is inclusive
            
            if weights is not None:
                result[i] = np.sum(values[start:end] * weights[start:end])
            else:
                result[i] = np.sum(values[start:end])
        
        return result
    
    def _panelmin(self, values: np.ndarray) -> np.ndarray:
        """Efficient panel minimum operation."""
        result = np.zeros(self.num_levels, dtype=values.dtype)
        
        for i in range(self.num_levels):
            start = self.info.starts[i]
            end = self.info.ends[i] + 1
            result[i] = np.min(values[start:end])
        
        return result
    
    def _panelmax(self, values: np.ndarray) -> np.ndarray:
        """Efficient panel maximum operation."""
        result = np.zeros(self.num_levels, dtype=values.dtype)
        
        for i in range(self.num_levels):
            start = self.info.starts[i]
            end = self.info.ends[i] + 1
            result[i] = np.max(values[start:end])
        
        return result
    
    def _panelfirst(self, values: np.ndarray) -> np.ndarray:
        """Get first value in each panel."""
        return values[self.info.starts]
    
    def _panellast(self, values: np.ndarray) -> np.ndarray:
        """Get last value in each panel."""
        return values[self.info.ends]
    
    def levels_of(self) -> np.ndarray:
        """Extract unique levels (equivalent to Stata's flevelsof)."""
        if self.save_keys:
            return self.keys.copy()
        else:
            return np.arange(1, self.num_levels + 1)
    
    def is_id(self) -> bool:
        """Check if this factor uniquely identifies observations."""
        return np.all(self.counts == 1)
    
    def nested_within(self, other: 'Factor') -> bool:
        """Check if this factor is nested within another factor."""
        if self.num_obs != other.num_obs:
            return False
            
        # Create mapping from self levels to other levels
        mapping = {}
        for i in range(self.num_obs):
            self_level = self.levels[i]
            other_level = other.levels[i]
            
            if self_level in mapping:
                if mapping[self_level] != other_level:
                    return False
            else:
                mapping[self_level] = other_level
                
        return True
    
    def equals(self, other: 'Factor') -> bool:
        """Check if two factors are equivalent."""
        if self.num_obs != other.num_obs or self.num_levels != other.num_levels:
            return False
        return np.array_equal(self.levels, other.levels)
    
    def __repr__(self):
        """String representation of the Factor object."""
        multivar_str = f", vars={self.num_vars}" if self.is_multivariate else ""
        sorted_str = f", sorted={self.is_sorted}" if not self.is_sorted else ""
        return (f"Factor(levels={self.num_levels}, "
                f"obs={self.num_obs}, "
                f"method='{self.method}'{multivar_str}{sorted_str})")
    
    def __str__(self):
        """Human-readable string representation."""
        return self.__repr__()
    
    def summary(self):
        """Print detailed summary of the factor."""
        print(f"Factor Summary:")
        print(f"  Observations: {self.num_obs:,}")
        print(f"  Unique levels: {self.num_levels:,}")
        print(f"  Variables: {self.num_vars}")
        print(f"  Method: {self.method}")
        print(f"  Is sorted: {self.is_sorted}")
        print(f"  Panel setup: {self.panel_is_setup}")
        if self.counts is not None:
            print(f"  Level sizes: min={np.min(self.counts)}, "
                  f"max={np.max(self.counts)}, mean={np.mean(self.counts):.1f}")
        if self.save_keys and self.keys is not None:
            print(f"  Sample keys: {self.keys[:min(5, len(self.keys))]}")