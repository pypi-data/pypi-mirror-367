#! /usr/bin/env python3
"""
Entity metric mode enum.
"""

import enum

from pypassist.enum.enum_str import EnumStrMixin


class EntityMetricMode(EnumStrMixin, enum.Enum):
    """Strategy for computing distances between entities from sequences."""

    ELEMENTWISE = enum.auto()  # Compare aligned elements
    ALLPAIRS = enum.auto()  # Compare all possible pairs
