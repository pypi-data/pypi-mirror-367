#!/usr/bin/env python3
"""
Static criterion.
"""

import logging

from .settings import StaticCriterion


LOGGER = logging.getLogger(__name__)


class StaticCriterionApplierMixin:
    """
    Mixin for filtering sequences and trajectories based on static data.
    """

    SETTINGS_DATACLASS = StaticCriterion

    def _match(self, sequence_or_trajectory):
        """
        Determine if a sequence or trajectory matches this criterion.

        Args:
            sequence_or_trajectory (Union[Sequence, Trajectory]):
                The sequence or trajectory to evaluate.

        Returns:
            bool: True if the sequence or trajectory matches the criterion,
                  False otherwise.
        """
        if sequence_or_trajectory.static_data is None:
            return False
        result = sequence_or_trajectory.static_data.query(self.settings.query)
        return not result.empty

    def _filter(self, pool, inplace=False):
        """
        Filter sequences or trajectories based on a given static criterion.

        Args:
            pool (Union[SequencePool, TrajectoryPool]):
                The sequence or trajectory pool to filter
            inplace (bool, optional):
                - True: Modify the current pool directly
                - False: Return a new filtered pool
                Defaults to False.

        Returns:
            Union[SequencePool, TrajectoryPool, None]:
                A pool with sequences or trajectories that match the criterion.
                None if inplace.
        """
        # Get IDs of sequences that match the criterion
        matching_ids = self._which(pool)
        return pool.subset(matching_ids, inplace=inplace)

    def _which(self, pool):
        """
        Get the IDs of sequences or trajectories that satisfy the pandas query.

        Args:
            pool (Union[SequencePool, TrajectoryPool]):
                The pool to evaluate.

        Returns:
            set: A set of sequence or trajectory IDs that satisfy the query.
        """
        if pool.static_data is None:
            return set()

        result = pool.static_data.query(self.settings.query)
        if result.empty:
            return set()

        id_column = pool.settings.id_column
        return set(result.index.get_level_values(id_column).unique())
