#!/usr/bin/env python3
"""
Base class for sequence criterion.
"""

from abc import abstractmethod

from ...base.applier import CriterionApplier
from .exception import EntityCriterionException, UnregisteredEntityCriterionTypeError


class EntityCriterionApplier(CriterionApplier):
    """
    Base class for all entity criterion.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "../type"

    def filter(self, sequence_or_pool, inplace=False, **kwargs):
        """
        Filter entities in a sequence or sequence pool.

        Args:
            sequence_or_pool: The sequence or sequence pool to filter.
            inplace (bool): Whether to modify the input in place.
            **kwargs: Additional keyword arguments to override criterion settings.

        Returns:
            Sequence or SequencePool: Filtered sequence or sequence pool or None if inplace.
        """
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            if self._is_sequence_pool_instance(sequence_or_pool):
                return self._filter_entities_on_pool(sequence_or_pool, inplace)
            if self._is_sequence_instance(sequence_or_pool):
                return self._filter_entities_on_sequence(sequence_or_pool, inplace)

            raise EntityCriterionException(
                f"Expected Sequence or SequencePool, got {sequence_or_pool!r}"
            )

    @abstractmethod
    def _filter_entities_on_pool(self, sequence_pool, inplace=False):
        """
        Filter entities in a sequence pool based on this criterion.

        Args:
            sequence_pool (SequencePool): The sequence pool to filter entities from.
            inplace (bool, optional): If True, modifies the input in place. Defaults to False.

        Returns:
            SequencePool: The filtered sequence pool or None if inplace.
        """

    @abstractmethod
    def _filter_entities_on_sequence(self, sequence, inplace=False):
        """
        Filter entities in a sequence based on this criterion.

        Args:
            sequence (Sequence): The sequence to filter entities from.
            inplace (bool, optional): If True, modifies the input in place. Defaults to False.

        Returns:
            Sequence: The filtered sequence or None if inplace.
        """

    def _update_sequence_with_filtered_data(
        self, sequence, filtered_data, inplace=False
    ):
        """
        Helper method to update a sequence with filtered data or create a new one.

        Args:
            sequence: The original sequence.
            filtered_data: The filtered data.
            inplace: Whether to modify in place.

        Returns:
            Sequence: The updated sequence or None if inplace.
        """
        if inplace:
            sequence._sequence_data = filtered_data
            sequence.clear_cache()
            return None

        return sequence.__class__(
            sequence.id_value,
            filtered_data,
            sequence.settings,
            sequence.metadata,
            sequence.static_data,
        )

    def _update_pool_with_filtered_data(
        self, sequence_pool, filtered_data, inplace=False
    ):
        """
        Helper method to update a sequence pool with filtered data or create a new one.

        Args:
            sequence_pool: The original sequence pool.
            filtered_data: The filtered data.
            inplace: Whether to modify in place.

        Returns:
            SequencePool: The updated sequence pool or None if inplace.
        """
        if inplace:
            sequence_pool._sequence_data = filtered_data
            sequence_pool.clear_cache()
            return None

        return sequence_pool.__class__(
            filtered_data,
            sequence_pool.settings,
            sequence_pool.metadata,
            sequence_pool.static_data,
        )

    @classmethod
    def _unregistered_criterion_error(cls, criterion_type, err):
        """Raise an error for an unregistered entity criterion with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredEntityCriterionTypeError(
            f"Unknown entity criterion: '{criterion_type}'. "
            f"Available criterion: {registered}"
        ) from err
