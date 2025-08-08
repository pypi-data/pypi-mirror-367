#!/usr/bin/env python3
"""
Sequence Criterion exceptions.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from ...base.exception import CriterionException


class SequenceCriterionException(CriterionException):
    """
    Sequence criterion exceptions.
    """


class UnregisteredSequenceCriterionTypeError(
    UnregisteredTypeError, SequenceCriterionException
):
    """
    Unregistered sequence criterion type error.
    """
