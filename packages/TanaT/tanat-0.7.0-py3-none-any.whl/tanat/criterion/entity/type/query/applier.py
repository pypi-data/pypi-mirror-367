#!/usr/bin/env python3
"""
Pandas query criterion implementation.
"""

import logging

from ...base.applier import EntityCriterionApplier
from ....mixin.query.applier import QueryCriterionApplierMixin

LOGGER = logging.getLogger(__name__)


class QueryEntityCriterionApplier(
    QueryCriterionApplierMixin, EntityCriterionApplier, register_name="query"
):
    """
    Criterion that applies a pandas query to the sequence data.
    """

    def _filter_entities_on_sequence(self, sequence, inplace=False):
        """
        Filter entities in a sequence based on this criterion.

        Args:
            sequence_pool (SequencePool): The sequence pool to filter entities from.
            inplace (bool, optional): If True, modifies the input in place. Defaults to False.

        Returns:
            SequencePool: The filtered sequence pool or None if inplace.
        """
        filtered_data = self._apply_query(sequence, inplace=False)
        return self._update_sequence_with_filtered_data(
            sequence, filtered_data, inplace
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
        filtered_data = self._apply_query(sequence_pool, inplace=False)
        return self._update_pool_with_filtered_data(
            sequence_pool, filtered_data, inplace
        )
