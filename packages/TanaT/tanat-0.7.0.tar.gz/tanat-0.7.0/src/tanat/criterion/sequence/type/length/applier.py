#!/usr/bin/env python3
"""
Length based criterion .
"""

import logging

import pandas as pd

from ...base.applier import SequenceCriterionApplier
from .settings import LengthCriterion


LOGGER = logging.getLogger(__name__)


class LengthSequenceCriterionApplier(SequenceCriterionApplier, register_name="length"):
    """
    A criterion class for filtering sequences based on their length.
    """

    SETTINGS_DATACLASS = LengthCriterion

    def _match_impl(self, sequence):
        """
        Determine if a sequence matches this criterion.

        Args:
            sequence (Sequence): The sequence to evaluate.

        Returns:
            bool: True if the sequence matches the criterion, False otherwise.
        """
        sequence_length = len(sequence)

        # Check each condition and return False as soon as any condition fails
        if self.settings.gt is not None and not sequence_length > self.settings.gt:
            return False

        if self.settings.ge is not None and not sequence_length >= self.settings.ge:
            return False

        if self.settings.lt is not None and not sequence_length < self.settings.lt:
            return False

        if self.settings.le is not None and not sequence_length <= self.settings.le:
            return False

        # If we made it here, all applicable conditions passed
        return True

    def _which_impl(self, sequence_pool):
        """
        Get the IDs of sequences that satisfy the length criterion.

        Args:
            sequence_pool: The sequence pool to evaluate.

        Returns:
            set: A set of sequence IDs that satisfy the length criterion.
        """
        df = sequence_pool.sequence_data
        sequence_settings = sequence_pool.settings
        id_column = sequence_settings.id_column

        # Count occurrences per ID
        counts = df.index.get_level_values(id_column).value_counts()
        mask = pd.Series(True, index=counts.index)

        # Apply greater than filter
        if self.settings.gt is not None:
            mask &= counts > self.settings.gt

        # Apply greater than or equal filter
        if self.settings.ge is not None:
            mask &= counts >= self.settings.ge

        # Apply less than filter
        if self.settings.lt is not None:
            mask &= counts < self.settings.lt

        # Apply less than or equal filter
        if self.settings.le is not None:
            mask &= counts <= self.settings.le

        return set(mask[mask].index)

    def _filter_impl(self, sequence_pool, inplace=False):
        """
        Apply the length-based filtering criterion to the given sequence pool.

        Args:
            sequence_pool: The sequence pool to filter.
            inplace (bool, optional): If True, modifies the current sequence pool
                in place. Defaults to False.

        Returns:
            SequencePool: A filtered sequence pool or None if inplace.
        """
        matching_ids = list(self.which(sequence_pool))
        return sequence_pool.subset(matching_ids, inplace=inplace)
