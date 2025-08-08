#!/usr/bin/env python3
"""
Static sequence criterion.
"""

from ...base.applier import SequenceCriterionApplier
from ....mixin.static.applier import StaticCriterionApplierMixin


class StaticSequenceCriterionApplier(
    StaticCriterionApplierMixin, SequenceCriterionApplier, register_name="static"
):
    """
    Static sequence criterion.
    """

    def _match_impl(self, sequence):
        """
        Internal implementation of match method.
        Call _match() from StaticCriterionMixin
        """
        return self._match(sequence)

    def _filter_impl(self, sequence_pool, inplace=False):
        """
        Internal implementation of filter sequence method.
        Call _filter() from StaticCriterionMixin
        """
        return self._filter(sequence_pool, inplace=inplace)

    def _which_impl(self, sequence_pool):
        """
        Internal implementation of which method.
        Call _which() from StaticCriterionMixin
        """
        return self._which(sequence_pool)
