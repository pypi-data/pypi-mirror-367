#!/usr/bin/env python3
"""
Length criterion.
"""

from typing import Optional

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ....base.settings import Criterion
from ....decorator.sequence import sequence_compatible
from .exception import ContradictoryLengthCriterionError


@viewer
@sequence_compatible
@dataclass
class LengthCriterion(Criterion):
    """
    Filter sequences based on their length.

    Provides flexible length-based filtering with multiple comparison
    operators for sequence selection.

    Args:
        gt (int, optional):
            Keep sequences with length strictly greater than this value.
        ge (int, optional):
            Keep sequences with length greater than or equal to this value.
        lt (int, optional):
            Keep sequences with length strictly less than this value.
        le (int, optional):
            Keep sequences with length less than or equal to this value.

    Example:
        # Filter sequences with 10 or fewer events
        LengthCriterion(le=10)
    """

    gt: Optional[int] = None  # greater than
    ge: Optional[int] = None  # greater than or equal to
    lt: Optional[int] = None  # less than
    le: Optional[int] = None  # less than or equal to

    _REGISTER_NAME = "length"

    def __post_init__(self):
        if self.gt is not None and self.ge is not None:
            raise ContradictoryLengthCriterionError(
                "Cannot use 'gt' and 'ge' operators simultaneously"
            )
        if self.lt is not None and self.le is not None:
            raise ContradictoryLengthCriterionError(
                "Cannot use 'lt' and 'le' operators simultaneously"
            )

        lower = self.gt if self.gt is not None else self.ge
        upper = self.lt if self.lt is not None else self.le
        if lower is not None and upper is not None and lower >= upper:
            raise ContradictoryLengthCriterionError(
                f"lower bound ({lower}) must be strictly less than upper bound ({upper})."
            )
