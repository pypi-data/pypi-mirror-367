#!/usr/bin/env python3
"""
Interval sequence pool class.
"""

from ...base.pool import SequencePool
from .sequence import IntervalSequence
from .settings import IntervalSequenceSettings


class IntervalSequencePool(SequencePool, register_name="interval"):
    """
    Sequence pool for interval sequences.
    """

    SETTINGS_DATACLASS = IntervalSequenceSettings

    def _create_sequence_instance(
        self, id_value, sequence_data, settings, metadata, static_data
    ):
        """Create IntervalSequence instance."""
        return IntervalSequence(
            id_value,
            sequence_data,
            settings,
            metadata,
            static_data,
        )
