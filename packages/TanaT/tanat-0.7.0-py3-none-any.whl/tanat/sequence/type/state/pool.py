#!/usr/bin/env python3
"""
State sequence pool class.
"""

from ....criterion.base.enum import CriterionLevel
from ....criterion.utils import resolve_and_init_criterion
from ...base.pool import SequencePool
from .sequence import StateSequence
from .settings import StateSequenceSettings


class StateSequencePool(SequencePool, register_name="state"):
    """
    Sequence pool for state sequences.
    """

    SETTINGS_DATACLASS = StateSequenceSettings

    def _create_sequence_instance(
        self, id_value, sequence_data, settings, metadata, static_data
    ):
        """Create StateSequence instance."""
        return StateSequence(
            id_value,
            sequence_data,
            settings,
            metadata,
            static_data,
        )

    def filter(
        self, criterion, level=None, inplace=False, criterion_type=None, **kwargs
    ):
        """
        Apply filtering to the sequence pool using the provided criterion.

        This method overrides the base `SequencePool.filter()` to explicitly prevent
        entity-level filtering, which is not supported for state sequences.

        Args:
            criterion (Union[Criterion, dict]):
                Filtering criterion as a `Criterion` object or a dictionary.
            level (str, optional):
                The level at which to apply the filter ("sequence" or "entity").
                Required when using a dictionary or if the criterion applies to multiple levels.
            inplace (bool, optional):
                If True, modifies the current pool in place. Defaults to False.
            criterion_type (str, optional):
                Type of criterion (e.g., "query", "pattern"). Required if using a dictionary.
            **kwargs:
                Extra keyword arguments to override criterion attributes.

        Returns:
            SequencePool:
                A new filtered sequence pool, or the modified one if `inplace=True`.

        Raises:
            ValueError:
                If required arguments are missing when `criterion` is a dictionary.
            NotImplementedError:
                If attempting entity-level filtering on state sequences.
        """
        # Ultimate one-liner: validate, resolve, and initialize criterion
        criterion, resolved_level = resolve_and_init_criterion(
            criterion, level, criterion_type, CriterionLevel.SEQUENCE
        )

        if resolved_level == CriterionLevel.ENTITY:
            raise NotImplementedError(
                "Entity level filtering is not supported for state sequences. "
                "Consider using interval sequences instead."
            )

        return criterion.filter(self, inplace, **kwargs)
