#!/usr/bin/env python3
"""
Exceptions raised by TrajectoryMetrics.
"""

from pypassist.mixin.registrable import UnregisteredTypeError

from ....exception import TanatException


class TrajectoryMetricException(TanatException):
    """
    Base class for exceptions raised by TrajectoryMetrics.
    """


class UnregisteredTrajectoryMetricTypeError(
    UnregisteredTypeError, TrajectoryMetricException
):
    """
    Exception raised when a trajectory metric type is not registered.
    """
