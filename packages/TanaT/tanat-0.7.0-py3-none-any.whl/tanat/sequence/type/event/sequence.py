#!/usr/bin/env python3
"""
Event sequence class.
"""

from ...base.sequence import Sequence
from .entity import EventEntity
from .settings import EventSequenceSettings


class EventSequence(Sequence, register_name="event"):
    """
    Event sequence.
    """

    SETTINGS_DATACLASS = EventSequenceSettings

    def _get_entity(self, data):
        """
        Get an entity instance.
        """
        return EventEntity(data, self._settings)
