#!/usr/bin/env python3
"""Interval data transformer."""

import logging

from ..period.base import PeriodDataTransformer

LOGGER = logging.getLogger(__name__)


class IntervalDataTransformer(PeriodDataTransformer, register_name="interval"):
    """Transformer for interval sequences."""

    def _get_anchor_for_relative_data(self):
        """Intervals use configurable anchor from settings."""
        return self.sequence_settings.anchor

    def _standardized_data(self, drop_na, entity_features=None):
        """Process interval data using basic standardization pattern."""
        return self._get_basic_standardized_data(drop_na, entity_features)

    def _to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """Distribution not supported for intervals."""
        raise NotImplementedError(
            f"to_distribution() is not supported for {type(self).__name__}"
        )
