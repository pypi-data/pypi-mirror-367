#!/usr/bin/env python3
"""
Exceptions raised by SequenceMetrics.
"""

from pypassist.mixin.registrable import UnregisteredTypeError

from ....exception import TanatException


class SequenceMetricException(TanatException):
    """
    Base class for exceptions raised by SequenceMetrics.
    """


class UnregisteredSequenceMetricTypeError(
    UnregisteredTypeError, SequenceMetricException
):
    """
    Exception raised when a sequence metric type is not registered.
    """
