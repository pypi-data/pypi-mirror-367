#!/usr/bin/env python3
"""
Length criterion exception.
"""

from ....base.exception import CriterionException


class ContradictoryLengthCriterionError(CriterionException):
    """
    Raised when length-based filtering criterion are logically incompatible.

    This exception occurs during length criterion configuration when:
    - Attempting to use both 'gt' and 'ge' operators simultaneously
    - Attempting to use both 'lt' and 'le' operators simultaneously
    - Specifying lower and upper bounds that create an impossible condition
      (e.g., lower bound is greater than or equal to upper bound)

    Prevents silent failures in sequence length filtering by explicitly
    highlighting configuration errors.
    """
