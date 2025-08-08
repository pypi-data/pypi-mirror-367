#!/usr/bin/env python3
"""
Exceptions for aggregation functions.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from ....exception import TanatException


class AggregationFunctionException(TanatException):
    """
    Base class for exceptions raised by aggregation functions.
    """


class UnregisteredAggregationFunctionTypeError(
    UnregisteredTypeError, AggregationFunctionException
):
    """
    Exception raised when an aggregation function is not registered.
    """
