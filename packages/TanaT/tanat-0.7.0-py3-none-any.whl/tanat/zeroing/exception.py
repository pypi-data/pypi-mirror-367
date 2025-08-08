#!/usr/bin/env python3
"""
Base class for zero setter exceptions.
"""

from pypassist.mixin.registrable import UnregisteredTypeError

from ..exception import TanatException


class ZeroSetterException(TanatException):
    """Base class for zero setter exceptions."""


class UnregisteredZeroSetterTypeError(UnregisteredTypeError, ZeroSetterException):
    """Exception raised when a zero setter type is not registered."""
