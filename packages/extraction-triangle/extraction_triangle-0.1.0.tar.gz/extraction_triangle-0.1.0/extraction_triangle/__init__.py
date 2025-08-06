"""
Extraction Triangle Library

A Python library for creating right triangle plots for extraction data visualization.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .triangle_plot import RightTrianglePlot
from .coordinates import RightTriangleCoordinates
from .utils import validate_data, normalize_data

__all__ = [
    "RightTrianglePlot",
    "RightTriangleCoordinates", 
    "validate_data",
    "normalize_data"
]
