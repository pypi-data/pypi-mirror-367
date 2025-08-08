#!/usr/bin/env python3
"""
Interval sequence type settings.
"""

import dataclasses

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ...settings.base import BaseSequenceSettings
from ...settings.static_feature import StaticFeatureSettings
from ...settings.temporal import TemporalSettings
from ....time.anchor import DateAnchor


@dataclasses.dataclass
class IntervalTemporalSettings(TemporalSettings):
    """
    Temporal configuration for interval sequences.

    Manages start/end time columns and anchor points for interval-based
    sequences. Controls temporal ordering and interval representation.

    Attributes:
        start_column (str): Column containing interval start times.
        end_column (str): Column containing interval end times or durations.
        anchor (DateAnchor): Temporal anchor for ordering intervals:
            - START: Use interval start time (default)
            - END: Use interval end time
            - MIDDLE: Use interval midpoint
    """

    start_column: str
    end_column: str
    anchor: DateAnchor = DateAnchor.START

    def temporal_columns(self, standardize=False):  # pylint: disable=unused-argument
        """
        Return the list of temporal columns, including start and end time columns.

        Args:
            standardize:
                Useless here, but kept for consistency with other types.

        Returns:
            A list of column names.
        """
        return [self.start_column, self.end_column]


@viewer
@dataclass
class IntervalSequenceSettings(
    StaticFeatureSettings,
    IntervalTemporalSettings,
    BaseSequenceSettings,
):
    """
    Complete configuration for interval sequences.

    Attributes:
        id_column (str): Column containing sequence identifiers.
        entity_features (List[str]): Columns for interval entity features
            (types, categories, values, etc.).
        start_column (str): Column containing interval start times.
        end_column (str): Column containing interval end times or durations.
        anchor (DateAnchor): Temporal anchor for interval ordering:
            - START: Order by interval start time (default)
            - END: Order by interval end time
            - MIDDLE: Order by interval midpoint
        static_features (Optional[List[str]]): Columns for static features.

    Note: Inherits temporal columns, entity features, and static features
    from respective mixin classes.

    Examples:
        >>> # Basic interval settings
        >>> settings = IntervalSequenceSettings(
        ...     id_column="patient_id",
        ...     entity_features=["medication"],
        ...     start_column="start_date",
        ...     end_column="end_date"
        ... )

        >>> # Interval settings with middle anchor and static features
        >>> settings = IntervalSequenceSettings(
        ...     id_column="patient_id",
        ...     entity_features=["treatment_type"],
        ...     start_column="admission_date",
        ...     end_column="discharge_date",
        ...     anchor="middle",
        ...     static_features=["age", "gender"]
        ... )

        >>> # Multiple entity features with end anchor
        >>> settings = IntervalSequenceSettings(
        ...     id_column="session_id",
        ...     entity_features=["activity", "location", "intensity"],
        ...     start_column="start_time",
        ...     end_column="end_time",
        ...     anchor="end"
        ... )
    """
