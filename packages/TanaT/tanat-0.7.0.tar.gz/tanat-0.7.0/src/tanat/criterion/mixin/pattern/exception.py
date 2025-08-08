#!/usr/bin/env python3
"""
Exceptions for pattern criterion.
"""

from ...base.exception import CriterionException


class InvalidColumnPatternError(CriterionException):
    """
    Raised when an invalid or non-existent column is used in pattern matching.

    This exception occurs during pattern-based filtering when a specified column
    does not exist in the target DataFrame.

    Helps prevent silent failures in pattern matching by explicitly
    highlighting column-related configuration errors.
    """
