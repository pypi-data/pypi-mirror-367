#!/usr/bin/env python3
"""
Time criterion mixin.
"""

import logging

import pandas as pd

from tanat.criterion.mixin.time.settings import TimeCriterion


LOGGER = logging.getLogger(__name__)


class TimeCriterionApplierMixin:
    """
    Mixin for applying flexible time-based filtering to temporal data.
    """

    SETTINGS_DATACLASS = TimeCriterion

    def _convert_datetime(self, series):
        """
        Convert a pandas Series to datetime using the configured date format, if provided.
        Returns the original series if no format is set.
        """
        if self.settings.date_format:
            return pd.to_datetime(
                series, format=self.settings.date_format, errors="coerce"
            )
        return series

    def _filter_event(self, df, time_col):
        """
        Apply point-in-time filters (events) to a single timestamp column.
        Returns a boolean mask of the filtered rows.
        """
        series = self._convert_datetime(df[time_col])
        mask = pd.Series(True, index=df.index)

        if self.settings.start_after:
            mask &= series > self.settings.start_after
        if self.settings.end_before:
            mask &= series < self.settings.end_before
        if self.settings.start_before:
            mask &= series < self.settings.start_before
        if self.settings.end_after:
            mask &= series > self.settings.end_after

        return mask

    def _filter_interval(self, df, start_col, end_col):
        """
        Apply interval/state filters to start and end timestamp columns.
        Returns a boolean mask of the filtered rows.

        Args:
            df: DataFrame containing the data
            start_col: Column name for start timestamps
            end_col: Column name for end timestamps

        Returns:
            pd.Series: Boolean mask for filtered rows
        """
        start_series = self._convert_datetime(df[start_col])
        end_series = self._convert_datetime(df[end_col])

        if self.settings.duration_within:
            return self._strict_containment_mask(start_series, end_series)
        return self._overlap_mask(start_series, end_series)

    def _strict_containment_mask(self, start_series, end_series):
        """
        Entity duration must be fully contained within ALL specified bounds.

        Args:
            start_series: Series of start timestamps
            end_series: Series of end timestamps

        Returns:
            pd.Series: Boolean mask where True means entity is fully contained
        """
        mask = pd.Series(True, index=start_series.index)

        # Entity start must be within bounds
        if self.settings.start_after is not None:
            mask &= start_series >= self.settings.start_after
        if self.settings.start_before is not None:
            mask &= start_series < self.settings.start_before

        # Entity end must be within bounds
        if self.settings.end_after is not None:
            mask &= end_series >= self.settings.end_after
        if self.settings.end_before is not None:
            mask &= end_series < self.settings.end_before

        return mask

    def _overlap_mask(self, start_series, end_series):
        """
        Entity can partially overlap with specified bounds.
        Uses standard interval overlap logic: two intervals overlap if
        start1 < end2 AND end1 > start2

        Args:
            start_series: Series of start timestamps
            end_series: Series of end timestamps

        Returns:
            pd.Series: Boolean mask where True means entity overlaps with criterion
        """
        mask = pd.Series(True, index=start_series.index)

        # Define filter boundaries
        filter_start = self.settings.start_after
        filter_end = self.settings.end_before

        # Apply overlap logic for the main range
        if filter_start is not None or filter_end is not None:
            if filter_start is not None:
                # Entity end must be after filter start
                mask &= end_series > filter_start
            if filter_end is not None:
                # Entity start must be before filter end
                mask &= start_series < filter_end

        # Apply additional individual constraints
        if self.settings.start_before is not None:
            mask &= start_series < self.settings.start_before
        if self.settings.end_after is not None:
            mask &= end_series > self.settings.end_after

        return mask

    def _apply_time_filters(self, df, time_columns):
        """
        Main entry point to apply time-based filters to a DataFrame.

        If one temporal column is provided, it is treated as a point-in-time event.
        If two columns are provided, they are treated as an interval or state.
        """
        if len(time_columns) == 1:
            return self._filter_event(df, time_columns[0])

        ## 2 columns => interval/state
        return self._filter_interval(df, time_columns[0], time_columns[1])
