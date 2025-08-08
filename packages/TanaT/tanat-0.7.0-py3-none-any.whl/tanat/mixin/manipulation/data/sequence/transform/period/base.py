#!/usr/bin/env python3
"""Base transformer for period-based sequences (intervals and states)."""

import logging
from abc import abstractmethod

from ..base import SequenceDataTransformer
from .......time.anchor import resolve_date_series_from_anchor
from .......time.duration import calculate_duration_from_series

LOGGER = logging.getLogger(__name__)


class PeriodDataTransformer(SequenceDataTransformer):
    """
    Base transformer for period-based sequences with start and end times.
    Provides shared logic for intervals and states transformations.
    """

    def _to_relative_time(
        self,
        drop_na=False,
        entity_features=None,
        tmp_t0_col="__TMP_T0__",
    ):
        """Transform period data to relative time based on t_zero."""
        sequence_data_copy = self._standardized_data(
            drop_na=drop_na, entity_features=entity_features
        )
        if not drop_na:
            sequence_data_copy = sequence_data_copy.copy()

        t_zero = self._sequence.t_zero
        sequence_data_copy = self._add_t0_column(sequence_data_copy, t_zero, tmp_t0_col)
        sequence_settings = self.sequence_settings

        start_column, end_column = sequence_settings.temporal_columns(standardize=True)

        granularity = self._sequence.granularity
        relative_start = calculate_duration_from_series(
            start_series=sequence_data_copy[tmp_t0_col],
            end_series=sequence_data_copy[start_column],
            granularity=granularity,
        )
        relative_end = calculate_duration_from_series(
            start_series=sequence_data_copy[tmp_t0_col],
            end_series=sequence_data_copy[end_column],
            granularity=granularity,
        )

        sequence_data_copy[start_column] = relative_start.values
        sequence_data_copy[end_column] = relative_end.values

        col2drop = [tmp_t0_col]
        return self._cleanup_temporal_columns(sequence_data_copy, col2drop)

    def _standardize_relative_data(self, drop_na=False, entity_features=None):
        """Standardize relative data for period sequences."""
        tmp_t0_col = "__TMP_T0__"
        sequence_data_copy = self._standardized_data(
            drop_na=drop_na, entity_features=entity_features
        )
        if not drop_na:
            sequence_data_copy = sequence_data_copy.copy()

        t_zero = self._sequence.t_zero
        sequence_data_copy = self._add_t0_column(sequence_data_copy, t_zero, tmp_t0_col)
        sequence_settings = self.sequence_settings
        temporal_columns = sequence_settings.temporal_columns(standardize=True)

        anchor = self._get_anchor_for_relative_data()
        anchor_date = resolve_date_series_from_anchor(
            sequence_data_copy, temporal_columns, anchor
        )

        granularity = self._sequence.granularity
        relative_time = calculate_duration_from_series(
            start_series=sequence_data_copy[tmp_t0_col],
            end_series=anchor_date,
            granularity=granularity,
        )

        relative_time_column = self.settings.relative_time_column
        sequence_data_copy[relative_time_column] = relative_time.values

        col2drop = temporal_columns + [tmp_t0_col]
        return self._cleanup_temporal_columns(sequence_data_copy, col2drop)

    def _to_time_spent(
        self, by_id=False, granularity="day", drop_na=False, entity_features=None
    ):
        """Transform sequence data to time spent for period sequences."""
        return self._compute_time_spent_for_period_sequences(
            by_id=by_id,
            granularity=granularity,
            drop_na=drop_na,
            entity_features=entity_features,
        )

    @abstractmethod
    def _get_anchor_for_relative_data(self):
        """
        Get the anchor point for relative data calculation.

        Returns:
            str: Anchor point ("start", "end", "middle")
        """
