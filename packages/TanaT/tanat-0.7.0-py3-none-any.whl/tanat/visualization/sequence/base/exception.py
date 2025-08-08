#!/usr/bin/env python3
"""
Base exceptions for sequence visualization.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError
from ....exception import TanatException


class SequenceVisualizationException(TanatException):
    """Base class for sequence visualization exceptions."""


class UnregisteredVisualizationTypeError(
    UnregisteredTypeError, SequenceVisualizationException
):
    """Exception raised when a visualization type is not registered."""
