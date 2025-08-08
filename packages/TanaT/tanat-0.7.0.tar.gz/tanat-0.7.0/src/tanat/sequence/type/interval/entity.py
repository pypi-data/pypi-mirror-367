#!/usr/bin/env python3
"""
Interval entity class.
"""

from ...base.entity import Entity, PeriodExtent
from .settings import IntervalSequenceSettings


class IntervalEntity(Entity):
    """
    Interval entity.
    """

    SETTINGS_DATACLASS = IntervalSequenceSettings

    def _get_temporal_extent(self):
        start = self._data[self.settings.start_column]
        end = self._data[self.settings.end_column]
        return PeriodExtent(start, end)
