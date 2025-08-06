"""Package with example functions and classes demonstrating numpy-style docstrings.

This package provides examples of well-documented Python code using numpy-style
docstrings that are automatically converted to beautiful API documentation using
Sphinx and Napoleon.
"""

from importlib.metadata import version

from .hello_world import Calculator, calculate_statistics, hello_world

__version__ = version("cvx-package-template")

__all__ = ["Calculator", "calculate_statistics", "hello_world"]
