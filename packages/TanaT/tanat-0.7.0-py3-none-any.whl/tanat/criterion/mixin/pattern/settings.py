#!/usr/bin/env python3
"""
Pattern criterion.
"""

from typing import Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict, List

from ...base.settings import Criterion
from ...decorator.entity import entity_compatible
from ...decorator.sequence import sequence_compatible
from .enum import PatternOperator


@viewer
@entity_compatible
@sequence_compatible
@dataclass
class PatternCriterion(Criterion):
    """
    Flexible pattern-based filtering for sequences and entities.

    Enables complex pattern matching across data columns with advanced
    configuration options.

    Args:
        pattern (Dict[str, Union[str, List[str]]]):
            Column patterns to match. Supports:
            - Plain strings
            - Lists of strings
            - Regex patterns (prefix with 'regex:')

        contains (bool, optional):
            - True: Include sequences matching pattern
            - False: Exclude sequences matching pattern
            Defaults to True.

        case_sensitive (bool, optional):
            Whether matching is case-sensitive. Defaults to True.

        operator (PatternOperator, optional):
            Logical operator between patterns:
            - AND: All patterns must match
            - OR: At least one pattern matches
            Defaults to AND.

    Example:
        # Find sequences with emergency events
        PatternCriterion(pattern={'event_type': 'EMERGENCY'})
    """

    pattern: Dict[str, Union[str, List[str]]]
    contains: bool = True
    case_sensitive: bool = True
    operator: PatternOperator = PatternOperator.AND

    _REGISTER_NAME = "pattern"
