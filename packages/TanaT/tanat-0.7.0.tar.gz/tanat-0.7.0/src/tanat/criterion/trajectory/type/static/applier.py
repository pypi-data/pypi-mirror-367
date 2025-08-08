#!/usr/bin/env python3
"""
Static sequence criterion.
"""

from ....mixin.static.applier import StaticCriterionApplierMixin
from ...base.applier import TrajectoryCriterionApplier


class StaticTrajectoryCriterionApplier(
    StaticCriterionApplierMixin, TrajectoryCriterionApplier, register_name="static"
):
    """
    Static trajectory criterion.
    """

    def _match_impl(self, trajectory):
        """
        Internal implementation of match method.
        Call _match() from StaticCriterionMixin
        """
        return self._match(trajectory)

    def _filter_impl(self, trajectory_pool, inplace=False):
        """
        Internal implementation of filter trajectory method.
        Call _filter() from StaticCriterionMixin
        """
        return self._filter(trajectory_pool, inplace=inplace)

    def _which_impl(self, trajectory_pool):
        """
        Internal implementation of which method.
        Call _which() from StaticCriterionMixin
        """
        return self._which(trajectory_pool)
