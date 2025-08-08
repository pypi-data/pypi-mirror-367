#!/usr/bin/env python3
"""
Criterion exceptions.
"""

from ...exception import TanatException


class CriterionException(TanatException):
    """
    Base exception for all criterion-related errors in the TanaT framework.
    """


class InvalidCriterionError(CriterionException):
    """
    Raised when an invalid or improperly configured criterion is encountered.
    """
