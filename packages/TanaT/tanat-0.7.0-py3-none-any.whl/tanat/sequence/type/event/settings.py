#!/usr/bin/env python3
"""
Event sequence type settings.
"""

import dataclasses

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ...settings.base import BaseSequenceSettings
from ...settings.static_feature import StaticFeatureSettings
from ...settings.temporal import TemporalSettings


@dataclasses.dataclass
class EventTemporalSettings(TemporalSettings):
    """
    Temporal configuration for point-in-time events.

    Manages single timestamp columns for event-based sequences.
    Events represent discrete occurrences at specific time points.

    Attributes:
        time_column (str): Column containing event timestamps.
    """

    time_column: str

    def temporal_columns(self, standardize=False):  # pylint: disable=unused-argument
        """
        Return the list of temporal columns: time column.

        Args:
            standardize:
                Useless here, but kept for consistency with other types.

        Returns:
            A list of column names.
        """
        return [self.time_column]


@viewer
@dataclass
class EventSequenceSettings(
    StaticFeatureSettings,
    BaseSequenceSettings,
    EventTemporalSettings,
):
    """
    Complete configuration for event sequences.

    Attributes:
        id_column (str): Column containing sequence identifiers.
        time_column (str): Column containing event timestamps.
        entity_features (List[str]): Columns for event entity features
            (types, categories, values, etc.).
        static_features (Optional[List[str]]): Columns for static features.

    Note: Inherits temporal columns, entity features, and static features
    from respective mixin classes.

    Examples:
        >>> # Basic event settings
        >>> settings = EventSequenceSettings(
        ...     id_column="patient_id",
        ...     time_column="event_time",
        ...     entity_features=["event_type"]
        ... )

        >>> # Event settings with static features
        >>> settings = EventSequenceSettings(
        ...     id_column="user_id",
        ...     time_column="timestamp",
        ...     entity_features=["action", "category"],
        ...     static_features=["age", "location"]
        ... )

        >>> # Multiple entity features
        >>> settings = EventSequenceSettings(
        ...     id_column="session_id",
        ...     time_column="event_datetime",
        ...     entity_features=["event_name", "severity", "source"]
        ... )
    """
