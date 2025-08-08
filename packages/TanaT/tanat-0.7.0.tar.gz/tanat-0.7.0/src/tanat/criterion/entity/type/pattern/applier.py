#!/usr/bin/env python3
"""
Pattern criterion implementation for entity-level filtering.
"""

import logging

from ...base.applier import EntityCriterionApplier
from ....mixin.pattern.applier import PatternCriterionApplierMixin

LOGGER = logging.getLogger(__name__)


class PatternEntityCriterionApplier(
    PatternCriterionApplierMixin, EntityCriterionApplier, register_name="pattern"
):
    """
    Criterion for filtering entities based on pattern matching in multiple columns.

    This criterion can be used to include or exclude entities that contain
    specific patterns in specified columns. Patterns can be:
    - Strings: Simple substring matching
    - Strings with "regex:" prefix: Regular expression matching
    - Lists: For matching sequences of values in order
    """

    def _filter_entities_on_sequence(self, sequence, inplace=False):
        """
        Filter entities in a sequence based on this criterion.

        Args:
            sequence: The sequence to filter entities from.
            inplace: If True, modifies the input in place.

        Returns:
            Sequence: The filtered sequence or None if inplace.
        """
        # Validate pattern columns exist in the data
        self.validate_pattern_columns(sequence.sequence_data)

        # Apply pattern matching
        matches = self.apply_pattern_matching(sequence.sequence_data)

        # Invert matches if not contains
        if not self.settings.contains:
            matches = ~matches

        # Filter the data
        filtered_data = sequence.sequence_data.loc[matches]

        # Update or create new sequence with filtered data
        return self._update_sequence_with_filtered_data(
            sequence, filtered_data, inplace
        )

    def _filter_entities_on_pool(self, sequence_pool, inplace=False):
        """
        Filter entities in all sequences in a pool based on this criterion.

        Args:
            sequence_pool: The sequence pool to filter.
            inplace: If True, modifies the input in place.

        Returns:
            SequencePool: The filtered sequence pool or None if inplace.
        """
        # Validate pattern columns exist in the data
        self.validate_pattern_columns(sequence_pool.sequence_data)

        # Apply pattern matching directly to the pool data
        matches = self.apply_pattern_matching(sequence_pool.sequence_data)

        # Invert matches if not contains
        if not self.settings.contains:
            matches = ~matches

        # Filter the data
        filtered_data = sequence_pool.sequence_data.loc[matches]

        # Update or create new pool
        return self._update_pool_with_filtered_data(
            sequence_pool, filtered_data, inplace
        )
