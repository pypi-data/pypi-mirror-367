"""
Legacy compatibility module for backward compatibility.
This module provides the old Functions.SIP interface for existing code.
"""

# Import from the new sipa package structure
try:
    from sipa.core.colors import Colors
    from sipa.core.filters import Filters  
    from sipa.core.histogram import Histogram
    from sipa.core.rotate import Rotate
    from sipa.core.arithmetic import Aritmatich
except ImportError:
    # Fallback to local imports if sipa package not installed
    from .colors import Colors as LocalColors
    from .filters import Filters as LocalFilters
    from .hist import Histogram as LocalHistogram  
    from .rotate import Rotate as LocalRotate
    from .aritmatich import Aritmatich as LocalAritmatich
    
    # Use local versions
    Colors = LocalColors
    Filters = LocalFilters
    Histogram = LocalHistogram
    Rotate = LocalRotate
    Aritmatich = LocalAritmatich


