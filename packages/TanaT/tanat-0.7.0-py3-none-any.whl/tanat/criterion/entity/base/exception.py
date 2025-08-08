#!/usr/bin/env python3
"""
Entity Criterion exceptions.
"""

from pypassist.mixin.registrable.exceptions import UnregisteredTypeError

from ...base.exception import CriterionException


class EntityCriterionException(CriterionException):
    """
    Entity criterion exceptions.
    """


class UnregisteredEntityCriterionTypeError(
    UnregisteredTypeError, EntityCriterionException
):
    """
    Unregistered entity criterion type error.
    """
