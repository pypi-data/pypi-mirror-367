#!/usr/bin/env python3
"""
Base class for sequence exceptions.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError


from ...exception import TanatException


class SequenceException(TanatException):
    """Base class for sequence exceptions."""


class UnregisteredSequenceTypeError(UnregisteredTypeError, SequenceException):
    """Exception raised when a sequence type is not registered."""


class SequenceNotFoundError(SequenceException):
    """Exception raised when a sequence ID is not found."""
