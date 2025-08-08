#!/usr/bin/env python3
"""
Exceptions for data access mixins.
"""

from ....exception import TanatException


class DataAccessError(TanatException):
    """Base class for data access exceptions."""


class SequenceDataError(DataAccessError):
    """Exception raised for sequence data access errors."""


class StaticDataError(DataAccessError):
    """Exception raised for static data access errors."""
