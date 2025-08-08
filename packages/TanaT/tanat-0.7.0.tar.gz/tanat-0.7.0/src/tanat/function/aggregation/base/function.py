#!/usr/bin/env python3
"""
Base class for aggregation functions.
"""

from abc import abstractmethod

from ...base import Function
from .exception import UnregisteredAggregationFunctionTypeError


class AggregationFunction(Function):
    """
    Base class for aggregation functions.
    """

    _REGISTER = {}

    @abstractmethod
    def __call__(self, values):
        """
        Aggregate the values.

        Args:
            values (list):
                List of values to aggregate.

        Returns:
            float: The aggregated value.
        """

    @classmethod
    def _unregistered_function_error(cls, ftype, err):
        """Raise an error for an unregistered aggregation function with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredAggregationFunctionTypeError(
            f"Unknown aggregation function: '{ftype}'. "
            f"Available aggregation functions: {registered}"
        ) from err
