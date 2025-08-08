#!/usr/bin/env python3
"""
Enum for Timeline visualization.
"""

import enum

from pypassist.enum.enum_str import EnumStrMixin


class TimelineStackingMode(EnumStrMixin, enum.Enum):
    """
    Stacking modes for timeline visualizations.

    Defines how multiple sequences are arranged vertically in timeline plots
    to handle overlapping or parallel sequence display.

    Values:
        FLAT: Each sequence gets its own horizontal row. Best for showing
            individual sequence patterns without overlap.
        BY_CATEGORY: Sequences are stacked by their category/annotation.
            Sequences with same annotation share vertical space.
        AUTOMATIC: System chooses optimal stacking based on data
            characteristics and plot density.
    """

    FLAT = enum.auto()
    BY_CATEGORY = enum.auto()
    AUTOMATIC = enum.auto()


class TimelineMode(EnumStrMixin, enum.Enum):
    """
    Time modes for timeline visualizations.

    Defines whether timeline uses absolute timestamps or relative time
    scales for temporal alignment and comparison.

    Values:
        ABSOLUTE: Uses actual timestamps/dates. Shows sequences in their
            original temporal context with real dates/times.
        RELATIVE: Uses relative time starting from a common reference point.
            Useful for pattern comparison across sequences with different
            start times.
    """

    ABSOLUTE = enum.auto()
    RELATIVE = enum.auto()
