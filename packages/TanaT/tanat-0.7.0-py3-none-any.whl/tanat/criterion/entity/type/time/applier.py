#!/usr/bin/env python3
"""
Time criterion.
"""

import logging
import copy

from ...base.applier import EntityCriterionApplier
from ....mixin.time.applier import TimeCriterionApplierMixin


LOGGER = logging.getLogger(__name__)


class TimeEntityCriterionApplier(
    TimeCriterionApplierMixin, EntityCriterionApplier, register_name="time"
):
    """
    A criterion class for filtering time-based sequence data.
    """

    def _filter_entities_on_sequence(self, sequence, inplace=False):
        """
        Filter entities in a sequence based on this criterion.

        Args:
            sequence (Sequence): The sequence to filter entities from.
            inplace (bool, optional): If True, modifies the input in place. Defaults to False.

        Returns:
            Sequence: The filtered sequence or None if inplace.
        """
        sequence_settings = sequence.settings
        temporal_columns = sequence_settings.temporal_columns()
        df = sequence.sequence_data
        mask = self._apply_time_filters(df, temporal_columns)

        if inplace:
            # -- clear cache & return None
            sequence._sequence_data = df[mask]
            sequence.clear_cache()
            return None

        return sequence.__class__(
            sequence.id_value,
            df[mask],
            copy.deepcopy(sequence_settings),
            copy.deepcopy(sequence.metadata),
            sequence.static_data,
        )

    def _filter_entities_on_pool(self, sequence_pool, inplace=False):
        """
        Filter entities in a sequence pool based on this criterion.

        Args:
            sequence_pool (SequencePool): The sequence pool to filter entities from.
            inplace (bool, optional): If True, modifies the input in place. Defaults to False.

        Returns:
            SequencePool: The filtered sequence pool or None if inplace.
        """
        sequence_pool_settings = sequence_pool.settings
        temporal_columns = sequence_pool_settings.temporal_columns()
        df = sequence_pool.sequence_data
        mask = self._apply_time_filters(df, temporal_columns)

        new_sequence_data = df[mask]

        if inplace:
            sequence_pool._sequence_data = new_sequence_data
            sequence_pool.clear_cache()
            return None

        return sequence_pool.__class__(
            new_sequence_data,
            copy.deepcopy(sequence_pool_settings),
            copy.deepcopy(sequence_pool.metadata),
            sequence_pool.static_data,
        )
