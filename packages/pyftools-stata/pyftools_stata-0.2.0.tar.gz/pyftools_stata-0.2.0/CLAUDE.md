# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyFtools is a Python implementation of Stata's ftools package, providing fast data manipulation tools for categorical variables and group operations. The project is in early development with a core Factor class implemented and planned expansion to full ftools functionality.

## Architecture

- **Core Module**: `pyftools/factor.py` - Contains the main `Factor` class for efficient categorical variable handling
- **Entry Point**: `pyftools/__init__.py` - Package initialization exposing the Factor class
- **Reference**: `Stata_ftools_master/` - Complete original Stata source code for reference
- **Reference Files**: `Stata_ftools_ref_files/` - Text versions of Stata source files

The codebase follows a simple structure with the main implementation in the `pyftools/` directory. The Factor class uses numpy for efficient operations and provides pandas integration.

## Development Commands

### Installation and Setup
```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with test dependencies only
pip install -e ".[test]"
```

### Testing
```bash
# Run comprehensive test suite
python test_factor.py      # Test core Factor class
python test_fcollapse.py   # Test fcollapse functionality  
python test_ftools.py      # Test all ftools commands
python examples.py         # Run complete examples

# Run individual tests
python debug_factor.py     # Debug Factor operations

# Run tests using pytest (when available)
pytest

# Run tests with coverage
pytest --cov=pyftools
```

### Code Quality
```bash
# Format code with black
black pyftools/

# Run linting with flake8
flake8 pyftools/

# Type checking with mypy
mypy pyftools/
```

### Package Building
```bash
# Build package
python setup.py sdist bdist_wheel
```

## Core Implementation Details

### Factor Class (`pyftools/factor.py`)
- **Purpose**: Advanced categorical variable handling with multiple hashing strategies
- **Hashing Methods**: 
  - `hash0`: Perfect hashing for integer data (O(1) lookup, naturally sorted)
  - `hash1`: Open addressing hash table for general data (handles any data type)
  - `auto`: Intelligent algorithm selection based on data characteristics
- **Key Methods**: 
  - `__init__()`: Creates factor with optimal hashing method
  - `collapse()`: Group aggregation with panel operations (sum, mean, count, min, max, first, last)
  - `panelsetup()`: Efficient group boundary computation
  - `sort()` / `invsort()`: Permutation-based sorting operations
  - `levels_of()`: Extract unique keys (equivalent to flevelsof)
  - `is_id()`: Check if factor uniquely identifies observations
- **Performance**: O(N) operations with intelligent memory management

### Command Implementations

#### fcollapse (`pyftools/fcollapse.py`)
- **Purpose**: Fast aggregation equivalent to Stata's fcollapse
- **Features**: Multiple statistics, weighted aggregation, frequency counts
- **Integration**: Uses Factor class for efficient group operations

#### ftools Commands (`pyftools/ftools.py`)
- **fegen**: Fast group variable generation
- **flevelsof**: Extract unique levels with formatting options
- **fisid**: Validate unique identifiers  
- **fsort**: Pandas-optimized sorting with factor support
- **join_factors**: Efficient multi-dimensional factor combinations
- **fcount**: Group-based observation counting

### Dependencies
- **Core**: numpy>=1.19.0, pandas>=1.3.0
- **Development**: pytest, black, flake8, mypy, sphinx
- **Python**: 3.8+ compatibility

## Completed Implementation

All major ftools functionality has been implemented:
- ✅ `Factor` - Advanced categorical variable handling
- ✅ `fcollapse` - Fast collapse operations with all statistics
- ✅ `fegen` - Group identifier generation  
- ✅ `flevelsof` - Extract unique levels
- ✅ `fisid` - Identify unique observations
- ✅ `fsort` - Fast sorting operations
- ✅ `join_factors` - Multi-factor combinations
- ✅ `fcount` - Group-based counting

## Future Extensions

Potential additions for full parity:
- `fmerge` - Factor-based merge operations
- `freshape` - Efficient reshaping
- Advanced panel data operations
- Integration with statistical modeling libraries

## Development Notes

- Reference the original Stata implementation in `Stata_ftools_master/src/` for algorithm details
- Maintain compatibility with pandas DataFrames and numpy arrays
- Focus on O(N) performance characteristics
- Follow existing code style and type hints