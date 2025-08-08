#!/usr/bin/env python3
"""
State entity class.
"""

from ...base.entity import Entity, PeriodExtent
from .settings import StateSequenceSettings


class StateEntity(Entity):
    """
    State entity.
    """

    SETTINGS_DATACLASS = StateSequenceSettings

    def _get_temporal_extent(self):
        start, end = self.settings.temporal_columns(standardize=True)
        return PeriodExtent(self._data[start], self._data[end])
