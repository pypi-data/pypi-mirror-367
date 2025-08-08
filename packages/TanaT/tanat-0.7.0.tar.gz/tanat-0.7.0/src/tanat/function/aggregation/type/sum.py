#!/usr/bin/env python3
"""
Sum aggregation function.
"""

import logging

from numpy import sum as np_sum

from ..base.function import AggregationFunction

LOGGER = logging.getLogger(__name__)


class SumAggregationFunction(AggregationFunction, register_name="sum"):
    """
    Sum aggregation function.
    """

    def __init__(self, settings=None, *, workenv=None):
        if settings is not None:
            LOGGER.warning(
                "SumAggregationFunction does not support settings. Ignoring."
            )
            settings = None
        super().__init__(settings, workenv=workenv)

    def __call__(self, values):
        """
        Sum the values.

        Args:
            values (list):
                List of values to sum.

        Returns:
            float: The sum of the values.
        """
        return np_sum(values)
