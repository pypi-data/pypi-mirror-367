"""
Pythonic built-in functions for Dana.

This module provides Pythonic built-in functions (like len, sum, max, min, etc.)
for the Dana language using a central dispatch approach.

Copyright © 2025 Aitomatic, Inc.
MIT License
"""

from .function_factory import PythonicFunctionFactory, register_pythonic_builtins

__all__ = ["PythonicFunctionFactory", "register_pythonic_builtins"]
