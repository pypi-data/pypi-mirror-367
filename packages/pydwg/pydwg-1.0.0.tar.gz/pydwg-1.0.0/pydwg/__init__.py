"""
PyDWG - Drilling Pattern Generator

A Python package for generating drilling patterns for tunnel excavation 
based on AutoCAD polylines.
"""

__version__ = "1.0.0"
__author__ = "Sanjeev Bashyal"
__email__ = "sanjeev.bashyal01@gmail.com"

from .generator import FourSectionCutGenerator

__all__ = ["FourSectionCutGenerator"] 