#!/usr/bin/env python3
"""
Trajectory Criterion exceptions.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from ...base.exception import CriterionException


class TrajectoryCriterionException(CriterionException):
    """
    Trajectory criterion exceptions.
    """


class UnregisteredTrajectoryCriterionTypeError(
    UnregisteredTypeError, TrajectoryCriterionException
):
    """
    Unregistered trajectory criterion type error.
    """
