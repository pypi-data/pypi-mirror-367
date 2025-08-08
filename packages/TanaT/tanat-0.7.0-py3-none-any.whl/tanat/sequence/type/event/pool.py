#!/usr/bin/env python3
"""
Event sequence pool class.
"""

from ...base.pool import SequencePool
from .sequence import EventSequence
from .settings import EventSequenceSettings


class EventSequencePool(SequencePool, register_name="event"):
    """
    Sequence pool for event sequences.
    """

    SETTINGS_DATACLASS = EventSequenceSettings

    def _create_sequence_instance(
        self, id_value, sequence_data, settings, metadata, static_data
    ):
        """Create EventSequence instance."""
        return EventSequence(
            id_value,
            sequence_data,
            settings,
            metadata,
            static_data,
        )
