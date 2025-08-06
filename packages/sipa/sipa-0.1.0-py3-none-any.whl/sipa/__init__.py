"""
SIPA - Simple Image Processing Application

A PyQt5-based GUI application for simple image processing operations.
This package provides basic image processing functionality without using
advanced image processing libraries (except numpy).

Author: Haydar Kadıoğlu
"""

__version__ = "0.1.0"
__author__ = "Haydar Kadıoğlu"
__email__ = "haydarkadioglu@example.com"

from .core import (
    Colors,
    Filters,
    Histogram,
    Rotate,
    Aritmatich,
)

__all__ = [
    "Colors",
    "Filters", 
    "Histogram",
    "Rotate",
    "Aritmatich",
]
