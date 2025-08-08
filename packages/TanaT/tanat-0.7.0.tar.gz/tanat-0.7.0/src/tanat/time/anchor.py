#!/usr/bin/env python3
"""
Date anchor enumeration and anchor utilities for interval operations.
"""

import enum
import pandas as pd
from pypassist.enum.enum_str import EnumStrMixin


@enum.unique
class DateAnchor(EnumStrMixin, enum.Enum):
    """
    Date anchor strategies for intervals.

    Defines how to anchor intervals for ordering and reference:
    - START: Use interval start time
    - END: Use interval end time
    - MIDDLE: Use interval midpoint
    """

    START = enum.auto()
    END = enum.auto()
    MIDDLE = enum.auto()


def compute_anchor_date(start, end, anchor):
    """
    Compute anchored date based on start, end dates and anchor strategy.
    Works with both scalar values and pandas Series.

    Args:
        start: Start datetime (scalar or Series)
        end: End datetime (scalar or Series)
        anchor: The date anchoring strategy

    Returns:
        Datetime object or Series representing the anchored date(s)
    """
    anchor = _ensure_date_anchor(anchor)

    if anchor == DateAnchor.START:
        return start
    if anchor == DateAnchor.END:
        return end
    # DateAnchor.MIDDLE
    return start + (end - start) / 2


def resolve_date_from_anchor(df, temporal_columns, anchor, use_first=True):
    """
    Resolve date from dataframe slice and anchoring strategy.

    Args:
        df: Dataframe slice corresponding to one sequence
        temporal_columns: List of temporal columns
        anchor: The date anchoring strategy
        use_first: If True, uses first row, otherwise last

    Returns:
        Datetime object representing the date
    """
    anchor = _ensure_date_anchor(anchor)

    if df.empty:
        return None

    row = df.iloc[0] if use_first else df.iloc[-1]

    if len(temporal_columns) == 1:
        return row[temporal_columns[0]]

    start, end = row[temporal_columns[0]], row[temporal_columns[1]]
    return compute_anchor_date(start, end, anchor)


def resolve_date_series_from_anchor(df, temporal_columns, anchor):
    """
    Resolve dates from all rows using anchoring strategy.

    Args:
        df: Dataframe with temporal data
        temporal_columns: List of temporal columns
        anchor: The date anchoring strategy

    Returns:
        Pandas Series with datetime objects for each row
    """
    anchor = _ensure_date_anchor(anchor)

    if df.empty:
        return pd.Series([pd.NA] * len(df))

    if len(temporal_columns) == 1:
        return _ensure_series(df[temporal_columns[0]])

    start_series = df[temporal_columns[0]]
    end_series = df[temporal_columns[1]]
    result = compute_anchor_date(start_series, end_series, anchor)

    return _ensure_series(result)


def _ensure_date_anchor(anchor):
    """Ensure anchor is a DateAnchor enum."""
    return DateAnchor.from_str(anchor)


def _ensure_series(data):
    """Ensure input is a pandas Series."""
    if not isinstance(data, pd.Series):
        data = pd.Series(data)
    return data
