#!/usr/bin/env python3
"""
Exceptions raised by EntityMetrics.
"""

from pypassist.mixin.registrable import UnregisteredTypeError

from ....exception import TanatException


class EntityMetricException(TanatException):
    """
    Base class for exceptions raised by EntityMetrics.
    """


class UnregisteredEntityMetricTypeError(UnregisteredTypeError, EntityMetricException):
    """
    Exception raised when a entity metric type is not registered.
    """
