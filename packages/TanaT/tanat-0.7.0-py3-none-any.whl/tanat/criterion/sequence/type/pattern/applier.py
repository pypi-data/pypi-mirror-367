#!/usr/bin/env python3
"""
Pattern criterion implementation for sequence-level filtering.
"""

import logging

from ...base.applier import SequenceCriterionApplier
from ....mixin.pattern.applier import PatternCriterionApplierMixin

LOGGER = logging.getLogger(__name__)


class PatternSequenceCriterionApplier(
    PatternCriterionApplierMixin, SequenceCriterionApplier, register_name="pattern"
):
    """
    Criterion for filtering sequences based on pattern matching in multiple columns.

    This criterion can be used to include or exclude sequences that contain
    specific patterns in specified columns. Patterns can be:
    - Strings: Simple substring matching
    - Strings with "regex:" prefix: Regular expression matching
    - Lists: For matching sequences of values in order
    """

    def _match_impl(self, sequence):
        """
        Determine if a sequence matches this criterion.

        Args:
            sequence: The sequence to evaluate.

        Returns:
            bool: True if the sequence matches the criterion, False otherwise.
        """
        # Validate pattern columns exist in the data
        self.validate_pattern_columns(sequence.sequence_data)

        # Apply pattern matching
        matches = self.apply_pattern_matching(sequence.sequence_data)

        # Check if matches align with the "contains" flag
        has_matches = matches.any()
        return has_matches if self.settings.contains else not has_matches

    def _get_matching_ids(self, sequence_pool):
        """
        Helper method to get matching sequence IDs.
        Extracted common logic from _filter_impl and _which_impl.

        Args:
            sequence_pool: The sequence pool to evaluate.

        Returns:
            set: A set of matching sequence IDs.
        """
        sequence_data = sequence_pool.sequence_data

        # Validate pattern columns exist in the data
        self.validate_pattern_columns(sequence_data)

        # Apply pattern matching
        matches = self.apply_pattern_matching(sequence_data)

        # Group matches by sequence ID
        id_column = sequence_pool.settings.id_column
        matching_ids = set()

        # Process each unique ID
        index_data = sequence_data.index.get_level_values(id_column)
        for id_value in index_data.unique():
            id_mask = index_data == id_value
            id_matches = matches[id_mask]

            # Check if ID matches according to the "contains" flag
            has_matches = id_matches.any()
            if (has_matches and self.settings.contains) or (
                not has_matches and not self.settings.contains
            ):
                matching_ids.add(id_value)

        return matching_ids

    def _filter_impl(self, sequence_pool, inplace=False):
        """
        Filter sequences based on pattern matching.

        Args:
            sequence_pool: The sequence pool to filter.
            inplace: If True, modifies the current sequence pool in place.

        Returns:
            SequencePool: Filtered sequence pool or None if inplace.
        """
        # Get matching IDs
        matching_ids = list(self._get_matching_ids(sequence_pool))
        return sequence_pool.subset(matching_ids, inplace=inplace)

    def _which_impl(self, sequence_pool):
        """
        Get the IDs of sequences that match this criterion.

        Args:
            sequence_pool: The sequence pool to evaluate.

        Returns:
            set: Set of matching sequence IDs.
        """
        # Get matching IDs
        return self._get_matching_ids(sequence_pool)
