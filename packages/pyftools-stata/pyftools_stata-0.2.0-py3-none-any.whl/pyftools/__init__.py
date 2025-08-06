"""
PyFtools - Python implementation of ftools

Fast data manipulation tools inspired by Stata's ftools package.
"""

__version__ = "0.2.0"
__author__ = "Bryce Wang, Collin Liu"
__email__ = "brycew6m@stanford.edu, junnebailiu@gmail.com"

from .factor import Factor
from .fcollapse import fcollapse, fsum, fmean
from .ftools import fegen, flevelsof, fisid, fsort, join_factors, fcount

__all__ = ["Factor", "fcollapse", "fsum", "fmean", "fcount", 
          "fegen", "flevelsof", "fisid", "fsort", "join_factors"]
