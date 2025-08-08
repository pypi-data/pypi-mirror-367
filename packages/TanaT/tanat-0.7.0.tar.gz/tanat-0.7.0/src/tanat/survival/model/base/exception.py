#!/usr/bin/env python3
"""
Base class for sequence exceptions.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from ....exception import TanatException


class SurvivalModelException(TanatException):
    """Base class for survival model exceptions."""


class UnregisteredSurvivalModelTypeError(UnregisteredTypeError, SurvivalModelException):
    """Exception raised when a survival model type is not registered."""
