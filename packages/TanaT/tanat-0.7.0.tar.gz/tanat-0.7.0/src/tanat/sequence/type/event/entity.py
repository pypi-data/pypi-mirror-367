#!/usr/bin/env python3
"""
Event entity class.
"""

from ...base.entity import Entity, InstantExtent
from .settings import EventSequenceSettings


class EventEntity(Entity):
    """
    Event entity.
    """

    SETTINGS_DATACLASS = EventSequenceSettings

    def _get_temporal_extent(self):
        """
        Returns the extent of the entity.
        """
        return InstantExtent(
            self._data[self.settings.time_column],
        )
