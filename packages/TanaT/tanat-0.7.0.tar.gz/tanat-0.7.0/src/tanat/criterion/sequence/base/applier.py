#!/usr/bin/env python3
"""
Base class for sequence criterion.
"""

from abc import abstractmethod

from ...base.applier import CriterionApplier
from .exception import (
    SequenceCriterionException,
    UnregisteredSequenceCriterionTypeError,
)


class SequenceCriterionApplier(CriterionApplier):
    """
    Base class for all sequence criterion appliers.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "../type"

    def match(self, sequence, **kwargs):
        """
        Determine if a sequence matches this criterion.

        Args:
            sequence (Sequence): The sequence to evaluate.
            **kwargs: Additional keyword arguments to override criterion settings.

        Returns:
            bool: True if the sequence matches the criterion, False otherwise.
        """
        if not self._is_sequence_instance(sequence):
            raise SequenceCriterionException(f"Expected Sequence, got {type(sequence)}")

        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            return self._match_impl(sequence)

    @abstractmethod
    def _match_impl(self, sequence):
        """
        Internal implementation of match method.
        """

    def filter(self, sequence_pool, inplace=False, **kwargs):
        """
        Filter sequences based on a given criterion.

        Args:
            sequence_pool (SequencePool): The sequence pool to filter
            inplace (bool, optional): If True, modifies the current sequence pool
                in place. Defaults to False.
            **kwargs: Additional keyword arguments to override criterion settings.

        Returns:
            SequencePool: A new sequence pool with sequences that match the criterion.
        """
        if not self._is_sequence_pool_instance(sequence_pool):
            raise SequenceCriterionException(
                f"Expected SequencePool, got {type(sequence_pool)}"
            )

        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            return self._filter_impl(sequence_pool, inplace)

    @abstractmethod
    def _filter_impl(self, sequence_pool, inplace=False):
        """
        Internal implementation of filter sequence method.
        """

    def which(self, sequence_pool, **kwargs):
        """
        Get the IDs of sequences that satisfy this criterion.

        Args:
            sequence_pool (SequencePool): The sequence pool to evaluate.
            **kwargs: Additional keyword arguments to override criterion settings.

        Returns:
            set: A set of sequence IDs that satisfy this criterion.
        """
        if not self._is_sequence_pool_instance(sequence_pool):
            raise SequenceCriterionException(
                f"Expected SequencePool, got {type(sequence_pool)}"
            )

        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            return self._which_impl(sequence_pool)

    @abstractmethod
    def _which_impl(self, sequence_pool):
        """
        Internal implementation of which method.
        """

    @classmethod
    def _unregistered_criterion_error(cls, criterion_type, err):
        """Raise an error for an unregistered sequence criterion with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredSequenceCriterionTypeError(
            f"Unknown sequence criterion: '{criterion_type}'. "
            f"Available criterion: {registered}"
        ) from err
