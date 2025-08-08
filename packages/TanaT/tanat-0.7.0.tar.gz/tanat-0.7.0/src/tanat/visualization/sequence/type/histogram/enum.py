#! /usr/bin/env python3
"""
Histogram visualization enum.
"""

import enum

from pypassist.enum.enum_str import EnumStrMixin


class HistoShowAs(EnumStrMixin, enum.Enum):
    """
    Display modes for histogram visualizations.

    Defines what values are shown in histogram bars - occurrence counts,
    frequencies, or time spent durations.

    Values:
        OCCURRENCE: Shows raw occurrence counts for each category.
            Best for understanding absolute frequency patterns.
        FREQUENCY: Shows relative frequencies or rates.
            Useful for normalized comparisons across categories.
        TIME_SPENT: Shows duration spent in each state/interval.
            Only applicable to state and interval sequences.
    """

    OCCURRENCE = enum.auto()
    FREQUENCY = enum.auto()
    TIME_SPENT = enum.auto()


class HistoBarOrder(EnumStrMixin, enum.Enum):
    """
    Bar ordering modes for histogram visualizations.

    Defines how bars are sorted in the histogram for optimal data
    presentation and pattern recognition.

    Values:
        ALPHABETIC: Sort bars alphabetically by category name.
            Provides consistent ordering across different datasets.
        ASCENDING: Sort bars by value in ascending order (low to high).
            Emphasizes progression from minimum to maximum values.
        DESCENDING: Sort bars by value in descending order (high to low).
            Highlights most significant categories first.
    """

    ALPHABETIC = enum.auto()
    ASCENDING = enum.auto()
    DESCENDING = enum.auto()


class HistoOrientation(EnumStrMixin, enum.Enum):
    """
    Orientation modes for histogram visualizations.

    Defines whether histogram bars are displayed vertically or horizontally
    for optimal space usage and readability.

    Values:
        VERTICAL: Traditional vertical bars with categories on x-axis
            and values on y-axis. Best for short category names.
        HORIZONTAL: Horizontal bars with categories on y-axis and
            values on x-axis. Better for long category names or
            when emphasizing value comparisons.
    """

    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()
