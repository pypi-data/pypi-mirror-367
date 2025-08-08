#!/usr/bin/env python3
"""
State sequence type settings.
"""

import logging
import dataclasses
from typing import Optional, Union
import datetime as dt

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ...settings.base import BaseSequenceSettings
from ...settings.static_feature import StaticFeatureSettings
from ...settings.temporal import TemporalSettings

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class StateTemporalSettings(TemporalSettings):
    """
    Temporal configuration for state sequences.

    Manages start times and optional end times for state-based sequences.
    States represent persistent conditions over time periods.

    Attributes:
        start_column (str): Column containing state start times.
        end_column (Optional[str]): Column containing state end times.
            If None, end times are inferred from next state's start time.
        default_end_value (Optional[Union[dt.datetime, int]]): Default
            value for final state when end_column is None. Can be:
            - None: Leave as missing value (default)
            - datetime: Specific end time (e.g., "2099-12-31")
            - int: Numeric sentinel value
    """

    start_column: str
    end_column: Optional[str] = None
    default_end_value: Optional[Union[dt.datetime, int]] = None
    _default_end_column: str = dataclasses.field(default="__END__", repr=False)

    def temporal_columns(self, standardize=False):
        """
        Return the start and end time columns.

        Args:
            standardize:
                If True, then the default end column will be included in the
                returned list if the end_column is not given.

        Returns:
            A list of column names.
        """
        columns = [self.start_column]
        if self.end_column:
            columns.append(self.end_column)
        elif standardize:
            columns.append(self._default_end_column)

        return columns

    def __post_init__(self):
        """Validate the default end value."""
        if self.end_column is None and self.default_end_value is None:
            LOGGER.warning(
                "No end_column specified and default_end_value is None. "
                "It is recommended to set default_end_value to handle the last state "
                "in each ID group, otherwise it will remain as missing value."
            )


@viewer
@dataclass
class StateSequenceSettings(
    StaticFeatureSettings,
    StateTemporalSettings,
    BaseSequenceSettings,
):
    """
    Complete configuration for state sequences.

    Attributes:
        id_column (str): Column containing sequence identifiers.
        entity_features (List[str]): Columns for state entity features
            (types, categories, values, etc.).
        start_column (str): Column containing state start times.
        end_column (Optional[str]): Column containing state end times.
            If None, end times inferred from next state's start time.
        default_end_value (Optional[Union[dt.datetime, int]]): Default
            value for final state when end_column is None.
        static_features (Optional[List[str]]): Columns for static features.

    Note: Inherits temporal columns, entity features, and static features
    from respective mixin classes.

    Examples:
        >>> # Basic state settings with explicit end column
        >>> settings = StateSequenceSettings(
        ...     id_column="patient_id",
        ...     entity_features=["diagnosis"],
        ...     start_column="admission_date",
        ...     end_column="discharge_date"
        ... )

        >>> # State settings with inferred end times
        >>> settings = StateSequenceSettings(
        ...     id_column="session_id",
        ...     entity_features=["status"],
        ...     start_column="start_time",
        ...     default_end_value=datetime(2099, 12, 31)
        ... )

        >>> # Multiple entity features with static data
        >>> settings = StateSequenceSettings(
        ...     id_column="device_id",
        ...     entity_features=["state", "mode", "level"],
        ...     start_column="timestamp",
        ...     static_features=["device_type", "location"]
        ... )
    """
