#!/usr/bin/env python3
"""
Time criterion.
"""

import logging

from ...base.applier import SequenceCriterionApplier
from ....mixin.time.applier import TimeCriterionApplierMixin

LOGGER = logging.getLogger(__name__)


class TimeSequenceCriterionApplier(
    TimeCriterionApplierMixin, SequenceCriterionApplier, register_name="time"
):
    """
    A criterion class for filtering time-based sequence data.
    """

    def _match_impl(self, sequence):
        """
        Determine if a sequence satisfies the time criterion.

        Args:
            sequence: The sequence to evaluate.

        Returns:
            bool: True if the sequence contains matching elements, False otherwise.
        """
        return bool(self._evaluate_time_criterion(sequence))

    def _which_impl(self, sequence_pool):
        """
        Get the IDs of sequences that satisfy the time criterion.

        Args:
            sequence_pool: The sequence pool to evaluate.

        Returns:
            set: A set of sequence IDs that satisfy the time criterion.
        """
        return self._evaluate_time_criterion(sequence_pool)

    def _evaluate_time_criterion(self, data_source):
        """
        Common logic to evaluate time criterion on a data source.

        Args:
            data_source: The sequence or sequence_pool to evaluate.

        Returns:
            set: A set of sequence IDs that satisfy the time criterion.
        """
        df = data_source._get_standardized_data()
        temporal_columns = data_source.settings.temporal_columns()
        entity_mask = self._apply_time_filters(df, temporal_columns)

        if self.settings.sequence_within:
            # -- ALL entities in sequence must satisfy criterion
            return self._get_sequences_fully_within(df, entity_mask)

        # -- AT LEAST ONE entity in sequence must satisfy criterion
        return set(df.loc[entity_mask].index)

    def _get_sequences_fully_within(self, df, entity_mask):
        """
        Return sequence IDs where ALL entities satisfy the time criterion.

        Args:
            df: Standardized DataFrame
            entity_mask: Boolean mask for entities that satisfy criterion

        Returns:
            set: Sequence IDs (index values) where all entities are valid
        """
        grouped = entity_mask.groupby(df.index)
        valid_sequences = grouped.all()
        return set(valid_sequences[valid_sequences].index)

    def _filter_impl(self, sequence_pool, inplace=False):
        """
        Apply the time-based filtering criterion to the given sequence pool.

        Args:
            sequence_pool: The sequence pool to filter.
            inplace (bool, optional): If True, modifies the current sequence pool
                in place. Defaults to False.

        Returns:
            SequencePool: Filtered sequence pool or None if inplace.
        """
        matching_ids = list(self.which(sequence_pool))
        return sequence_pool.subset(matching_ids, inplace=inplace)
