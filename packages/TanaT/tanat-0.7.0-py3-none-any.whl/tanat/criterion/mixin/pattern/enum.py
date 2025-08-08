#! /usr/bin/env python3
"""
Pattern logical operator enum.
"""

import enum

from pypassist.enum.enum_str import EnumStrMixin


class PatternOperator(EnumStrMixin, enum.Enum):
    """
    Logical operators for pattern matching across multiple columns.

    Defines how multiple pattern conditions are combined during filtering:
    - AND: All specified patterns must match
    - OR: At least one pattern must match

    Used in pattern-based filtering to control the logical combination
    of multiple column pattern conditions.
    """

    AND = enum.auto()
    OR = enum.auto()
