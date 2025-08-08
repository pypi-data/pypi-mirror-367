#!/usr/bin/env python3
"""
Pandas query criterion implementation.
"""

import logging

from ...base.applier import SequenceCriterionApplier
from ....mixin.query.applier import QueryCriterionApplierMixin

LOGGER = logging.getLogger(__name__)


class QuerySequenceCriterionApplier(
    QueryCriterionApplierMixin, SequenceCriterionApplier, register_name="query"
):
    """
    Criterion that applies a pandas query to the sequence data.
    """

    def _match_impl(self, sequence):
        """
        Determine if a sequence matches this criterion.

        Args:
            sequence (Sequence): The sequence to evaluate.

        Returns:
            bool: True if the sequence matches the criterion, False otherwise.
        """
        subset_data = self._apply_query(sequence, inplace=False)
        return not subset_data.empty

    def _filter_impl(self, sequence_pool, inplace=False):
        """
        Filter sequences in a sequence pool based on this criterion.

        Args:
            sequence_pool (SequencePool): The sequence pool to filter sequences from.
            inplace (bool, optional): If True, modifies the input in place. Defaults to False.

        Returns:
            SequencePool: The filtered sequence pool or None if inplace.
        """
        matched_ids = list(self._which_impl(sequence_pool))
        return sequence_pool.subset(matched_ids, inplace=inplace)

    def _which_impl(self, sequence_pool):
        """
        Get the IDs of sequences that satisfy the pandas query.

        Args:
            sequence_pool (SequencePool): The sequence pool to evaluate.

        Returns:
            set: A set of sequence IDs that satisfy the pandas query.
        """
        filtered_data = self._apply_query(sequence_pool, inplace=False)

        id_col = sequence_pool.settings.id_column
        matched_ids = filtered_data.index.get_level_values(id_col).unique()
        return set(matched_ids)
