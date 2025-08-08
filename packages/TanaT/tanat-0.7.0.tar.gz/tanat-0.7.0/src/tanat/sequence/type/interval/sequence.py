#!/usr/bin/env python3
"""
Interval sequence class.
"""

from ...base.sequence import Sequence
from .entity import IntervalEntity
from .settings import IntervalSequenceSettings


class IntervalSequence(Sequence, register_name="interval"):
    """
    Interval sequence.
    """

    SETTINGS_DATACLASS = IntervalSequenceSettings

    def _get_entity(self, data):
        return IntervalEntity(data, self._settings)
