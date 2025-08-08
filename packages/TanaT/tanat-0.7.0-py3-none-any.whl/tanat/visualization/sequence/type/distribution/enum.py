#!/usr/bin/env python3
"""
Distribution visualization enum.
"""

import enum

from pypassist.enum.enum_str import EnumStrMixin


class DistributionMode(EnumStrMixin, enum.Enum):
    """
    Distribution calculation modes for distribution visualizations.

    Defines how distribution values are calculated and displayed across
    time periods for temporal pattern analysis.

    Values:
        PERCENTAGE: Values displayed as percentages (0-100%).
            Shows relative proportions with intuitive percentage scale.
        COUNT: Raw count values for each category per time period.
            Shows absolute numbers useful for magnitude assessment.
        PROPORTION: Values as proportions (0-1).
            Shows relative proportions with decimal scale.
    """

    PERCENTAGE = enum.auto()
    COUNT = enum.auto()
    PROPORTION = enum.auto()
