#!/usr/bin/env python3
"""State data transformer."""

import logging
import pandas as pd

from ..period.base import PeriodDataTransformer
from .......time.granularity import Granularity
from .......visualization.sequence.type.distribution.enum import DistributionMode

LOGGER = logging.getLogger(__name__)


class StateDataTransformer(PeriodDataTransformer, register_name="state"):
    """Transformer for state sequences."""

    def _get_anchor_for_relative_data(self):
        """States always use start anchor for relative data."""
        return "start"

    def _standardized_data(self, drop_na, entity_features=None):
        """
        Process state data with automatic end time calculation.
        Sets end times from next state's start when end_column is None.
        """
        start_column = self.sequence_settings.start_column
        id_column = self.sequence_settings.id_column
        end_column = self.sequence_settings.end_column

        data = self._sequence.sequence_data
        needs_copy = False

        # Handle missing end times
        if end_column is None:
            needs_copy = True

        # Handle dropping NA values
        if drop_na:
            needs_copy = True

        # Create a copy only if necessary
        data_copy = data.copy() if needs_copy else data

        if end_column is None:
            # pylint: disable=protected-access
            end_col = self.sequence_settings._default_end_column
            default_end = self.sequence_settings.default_end_value
            data_copy[end_col] = data_copy.groupby(id_column, group_keys=False)[
                start_column
            ].shift(-1, fill_value=default_end)

        if drop_na:
            data_copy.dropna(how="any", inplace=True)

        col2keep = self.sequence_settings.get_sequence_data_columns(
            standardize=True, entity_features=entity_features
        )
        return data_copy[col2keep]

    def _to_distribution(
        self,
        granularity="day",
        mode="proportion",
        time_relative=False,
        drop_na=False,
        entity_features=None,
    ):
        """
        Transform state data to temporal distribution.

        For state sequences, we create a temporal grid and count how many
        sequences are in each state at each time period (occupation approach).

        Args:
            mode (str): Distribution mode ('proportion', 'percentage', 'count')
            time_relative (bool): Whether to use relative time
            drop_na (bool): Whether to drop rows with missing values
            entity_features (list, optional): List of entity features to include

        Returns:
            pd.DataFrame: Temporal distribution data in long format
        """
        # Normalize mode
        distribution_mode = DistributionMode.from_str(mode)

        if time_relative:
            granularity = "unit"  # Use unit granularity for relative time
            data = self._to_relative_time(
                drop_na=drop_na, entity_features=entity_features
            )
        else:
            data = self._standardized_data(
                drop_na=drop_na, entity_features=entity_features
            )

        # Get column names
        start_col, end_col = self.sequence_settings.temporal_columns(standardize=True)
        entity_features = self._validate_and_filter_entity_features(entity_features)
        entity_col = (
            entity_features[0] if len(entity_features) == 1 else "combined_entity"
        )

        if len(entity_features) > 1:
            data[entity_col] = data[entity_features].astype(str).agg("_".join, axis=1)

        granularity = Granularity.from_str(granularity)

        # Create complete time range (handles both dates and floats)
        if granularity == Granularity.UNIT:
            # For relative time or numeric data, create a range of floats
            min_time = data[start_col].min()
            max_time = data[end_col].max()
            step = 1
            date_range = pd.Index(range(int(min_time), int(max_time) + 1, step))
        else:
            # For datetime data, use date_range
            freq = granularity.pandas_freq
            date_range = pd.date_range(
                start=data[start_col].min(), end=data[end_col].max(), freq=freq
            )

        # Get all unique states
        unique_states = data[entity_col].unique()

        # Create occupation matrix: periods x states
        occupation_matrix = pd.DataFrame(0, index=date_range, columns=unique_states)

        # Fill occupation matrix: for each sequence, mark periods where it's active
        for _, row in data.iterrows():
            start_time = row[start_col]
            end_time = row[end_col]
            state = row[entity_col]

            # Skip if invalid dates
            if pd.isna(start_time) or pd.isna(end_time):
                continue

            # Mark periods where this state is active
            mask = (date_range >= start_time) & (date_range <= end_time)
            occupation_matrix.loc[mask, state] += 1

        # Convert to long format and calculate percentages
        result_data = []
        for time_period in occupation_matrix.index:
            period_total = occupation_matrix.loc[time_period].sum()

            for state in unique_states:
                count = occupation_matrix.loc[time_period, state]

                # Calculate value based on mode
                if distribution_mode == DistributionMode.COUNT:
                    value = count
                elif period_total > 0:  # Avoid division by zero
                    if distribution_mode == DistributionMode.PROPORTION:
                        value = count / period_total
                    else:  # PERCENTAGE
                        value = (count / period_total) * 100
                else:
                    value = 0.0

                result_data.append(
                    {
                        "time_period": time_period,
                        "annotation": state,
                        self.settings.distribution_column: value,
                    }
                )

        return pd.DataFrame(result_data)
