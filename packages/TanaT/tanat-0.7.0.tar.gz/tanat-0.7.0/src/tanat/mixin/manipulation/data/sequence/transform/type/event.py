#!/usr/bin/env python3
"""
Event data transformer.
"""

import logging

from ..base import SequenceDataTransformer
from .......time.duration import calculate_duration_from_series

LOGGER = logging.getLogger(__name__)


class EventDataTransformer(SequenceDataTransformer, register_name="event"):
    """
    Transformer for event sequences.
    """

    def _standardized_data(self, drop_na, entity_features=None):
        """Process event data using basic standardization pattern."""
        return self._get_basic_standardized_data(drop_na, entity_features)

    def _to_relative_time(
        self,
        drop_na=False,
        entity_features=None,
        tmp_t0_col="__TMP_T0__",
    ):
        """
        Transform event data to relative time based on t_zero.

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.
            tmp_t0_col (str, optional): Temporary t0 column name


        Returns:
            pd.DataFrame: Transformed data
        """
        # -- Set reference dates from t_zero
        sequence_data_copy = self._standardized_data(
            drop_na=drop_na, entity_features=entity_features
        )
        if not drop_na:  # make sure it is a copy
            sequence_data_copy = sequence_data_copy.copy()
        t_zero = self._sequence.t_zero
        sequence_data_copy = self._add_t0_column(sequence_data_copy, t_zero, tmp_t0_col)
        sequence_settings = self.sequence_settings

        # -- Calculate duration from t_zero to event timestamp
        granularity = self._sequence.granularity
        duration_series = calculate_duration_from_series(
            start_series=sequence_data_copy[tmp_t0_col],
            end_series=sequence_data_copy[sequence_settings.time_column],
            granularity=granularity,
        )

        relative_time_column = self.sequence_settings.time_column
        sequence_data_copy[relative_time_column] = duration_series.values

        # -- Clean up useless temporal columns
        col2drop = [tmp_t0_col]
        sequence_data_copy = self._cleanup_temporal_columns(
            sequence_data_copy, col2drop
        )

        return sequence_data_copy

    def _standardize_relative_data(self, drop_na=False, entity_features=None):
        """
        Standardize relative data for event sequences.

        Args:
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include.
                If None, all features specified in the sequence settings will be included.

        Returns:
            pd.DataFrame: Standardized DataFrame
        """
        relative_df = self._to_relative_time(
            drop_na=drop_na, entity_features=entity_features
        )
        relative_df.rename(
            columns={
                self.sequence_settings.time_column: self.settings.relative_time_column,
            },
            inplace=True,
        )
        return relative_df

    def _to_time_spent(
        self,
        by_id=False,
        granularity="day",
        drop_na=False,
        entity_features=None,
    ):
        """
        Transform sequence data to time spent for event sequences.

        For events, the duration is calculated as an occurrence.

        Args:
            by_id (bool): Whether to group by the id column.
            granularity (str): Time unit for the time spent values.
                Useless for events, but kept for consistency.
            drop_na (bool): Whether to drop rows with missing values.
            entity_features (list): List of entity features to include in the calculation.
            If None, all features specified in the sequence settings will be used.

        Returns:
            pd.DataFrame: DataFrame with time spent values.
        """
        entity_features = self._validate_and_filter_entity_features(entity_features)
        occurrence_data = self.to_occurrence(
            by_id=by_id,
            drop_na=drop_na,
            entity_features=entity_features,
        )
        result = occurrence_data.copy()
        occurrence_col = self.settings.occurrence_column
        time_spent_col = self.settings.time_spent_column
        result.rename(
            columns={occurrence_col: time_spent_col},
            inplace=True,
        )

        return result

    def _to_distribution(
        self,
        # pylint:disable=unused-argument
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Transform event data to temporal distribution.

        Not supported for event sequences.

        Raises:
            NotImplementedError: Always raised for event sequences
        """
        raise NotImplementedError(
            f"to_distribution() is currently only supported for StateSequencePool. "
            f"Current type: {type(self).__name__}"
        )
