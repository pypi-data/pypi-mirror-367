#!/usr/bin/env python3
"""
Exceptions for sequence data transformation.
"""

from ...exceptions import SequenceDataError


class TransformationError(SequenceDataError):
    """Exception raised for errors in sequence data transformation."""
