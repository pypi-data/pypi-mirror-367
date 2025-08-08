#!/usr/bin/env python3
"""
Survival analysis core class.
"""

import logging

import numpy as np
import pandas as pd

from .model.base.model import SurvivalModel
from .result import SurvivalResult
from ..mixin.summarizer.survival import SurvivalSummarizerMixin
from ..time.query import get_date_from_query
from ..time.duration import calculate_duration_from_series
from ..sequence.base.pool import SequencePool
from ..sequence.base.sequence import Sequence

LOGGER = logging.getLogger(__name__)


class SurvivalAnalysis(SurvivalSummarizerMixin):
    """Survival analysis."""

    def __init__(self, model_type, settings=None):
        self.model_type = model_type
        self._model = SurvivalModel.init(model_type, settings)
        self._last_result = None  # Store last result for summary

    @property
    def settings(self):
        """Get current generator settings.

        Returns:
            Settings object for the current generator.
        """
        return self._model.settings

    def update_settings(self, settings=None, **kwargs):
        """
        Update the model settings.

        Args:
            settings: New settings object to update from
            **kwargs: Individual settings to update using dot notation for nested attributes
        """
        self._model.update_settings(settings=settings, **kwargs)

    def view_settings(self, format_type="yaml", **kwargs):
        """
        Return a read-only view of the current settings for display purposes.

        Args:
            format_type: The format in which to display the settings.
            **kwargs: Additional display options.
        """
        return self._model.settings.view(format_type=format_type, **kwargs)

    @property
    def model(self):
        """Get the model instance."""
        return self._model.model

    def fit(self, sequence_pool, survival_array=None, **kwargs):
        """
        Fit the model to the provided data pool.

        Args:
            sequence_pool: Sequence pool containing the sequences to analyze.
            survival_array: Precomputed structured array.
            kwargs: Optional overrides for specific settings.

        Returns:
            self: Fitted SurvivalAnalysis instance
        """
        self._validate_sequence_pool(sequence_pool)

        with self._model.with_tmp_settings(**kwargs):
            y, list_ids = self._prepare_survival_data(sequence_pool, survival_array)
            data_x = self._prepare_static_data(sequence_pool, list_ids)

            self._model.fit(data_x, y)
            self._model.is_fitted = True
            return self

    def _prepare_survival_data(self, sequence_pool, survival_array):
        """Prepare survival array and sequence IDs."""
        if survival_array is not None:
            return survival_array, None

        result = self.get_survival_array(sequence_pool=sequence_pool)
        return result.survival_array, result.sequence_ids

    def _prepare_static_data(self, sequence_pool, list_ids):
        """Prepare static data for fitting."""
        data_x = sequence_pool.static_data
        if data_x is None:
            raise ValueError("Static data is required for survival analysis.")

        if list_ids is not None:
            data_x = data_x.loc[list_ids]

        return data_x

    def get_survival_array(self, sequence_pool, **kwargs):
        """
        Extract survival data and return structured results.

        Args:
            sequence_pool: Sequence pool containing the sequences to analyze.
            **kwargs: Optional overrides for specific settings.

        Returns:
            SurvivalResult: Complete survival analysis results.
        """
        self._validate_sequence_pool(sequence_pool)

        # Auto-resolve anchor if needed
        if self.settings.anchor is None:
            kwargs = self._auto_resolve_anchor(sequence_pool, kwargs)

        with self._model.with_tmp_settings(**kwargs):
            return self._execute_survival_pipeline(sequence_pool)

    def _auto_resolve_anchor(self, sequence_pool, kwargs):
        """Automatically resolve anchor if not provided."""
        if "anchor" not in kwargs:
            # pylint: disable=protected-access
            anchor = sequence_pool._resolve_anchor()
            kwargs["anchor"] = anchor
        return kwargs

    def _execute_survival_pipeline(self, sequence_pool):
        """Execute the complete survival analysis pipeline."""
        self._ensure_query()

        # Extract temporal data
        endpoint_dates = self._extract_endpoint_dates(sequence_pool)
        t_zeros = self._extract_t_zeros(sequence_pool)

        # Process and calculate
        observation_data = self._process_censoring(t_zeros, endpoint_dates)
        durations = self._calculate_durations(observation_data)

        # Create final array
        survival_array, sequence_ids = self._create_survival_array(
            durations, observation_data
        )

        # Build and store result
        result = SurvivalResult(
            survival_array=survival_array,
            sequence_ids=sequence_ids,
            endpoint_dates=endpoint_dates,
            t_zeros=t_zeros,
            durations=durations,
            observation_data=observation_data,
        )

        self._last_result = result
        return result

    def predict_survival_function(self, sequence_or_pool, return_array=False):
        """
        Predict survival functions for sequences or pools.

        Args:
            sequence_or_pool: Sequence or sequence pool to predict for
            return_array: Whether to return array format

        Returns:
            Survival function predictions
        """
        self._validate_sequence_or_pool(sequence_or_pool)

        static_data = self._extract_static_data_for_prediction(sequence_or_pool)
        return self._model.predict_survival_function(
            static_data, return_array=return_array
        )

    def _extract_static_data_for_prediction(self, sequence_or_pool):
        """Extract and validate static data for prediction."""
        static_data = sequence_or_pool.static_data
        if static_data is None:
            raise ValueError("Static data is required for survival analysis.")
        return static_data

    def _ensure_query(self):
        """
        Ensure that the endpoint query is set.

        Raises:
            ValueError: If endpoint query is not set.
        """
        if self.settings.query is None:
            raise ValueError(
                "Endpoint query must be set to launch survival analysis. "
                "Please provide a valid query using `update_settings` or pass the 'query' "
                "parameter to this method."
            )

    def _validate_sequence_pool(self, sequence_pool):
        """
        Validate the sequence pool.
        """
        if not isinstance(sequence_pool, SequencePool):
            raise ValueError(
                "sequence_pool must be an instance of SequencePool. "
                f"Got: {type(sequence_pool)}"
            )

    def _validate_sequence_or_pool(self, sequence_or_pool):
        """
        Validate the input is either a valid Sequence or SequencePool.
        """
        if not isinstance(sequence_or_pool, (SequencePool, Sequence)):
            raise ValueError(
                "Invalid `sequence_or_pool` provided. "
                "Expected an instance of Sequence or SequencePool. "
                f"Got type: {type(sequence_or_pool)}"
            )

    def _extract_endpoint_dates(self, sequence_pool):
        """Extract endpoint dates for each sequence by applying the query."""
        sequence_data = self._get_standardized_data(sequence_pool)
        temporal_columns = self._get_temporal_columns(sequence_pool)

        endpoint_dates = get_date_from_query(
            sequence_data=sequence_data,
            query=self.settings.query,
            temporal_columns=temporal_columns,
            anchor=self.settings.anchor,
            use_first=True,
        )

        return pd.Series(endpoint_dates)

    def _get_standardized_data(self, sequence_pool):
        """Get standardized sequence data."""
        # pylint: disable=protected-access
        return sequence_pool._get_standardized_data()

    def _get_temporal_columns(self, sequence_pool):
        """Get temporal columns configuration."""
        return sequence_pool.settings.temporal_columns(standardize=True)

    def _extract_t_zeros(self, sequence_pool):
        """
        Extract T zeros for each sequence.

        Args:
            sequence_pool (SequencePool): The sequence pool to analyze.

        Returns:
            pd.Series: Series containing T zeros indexed by sequence IDs.

        Raises:
            ValueError: If T zero is not available and no fallback is provided.
        """
        ref_date = sequence_pool.t_zero
        # Create a Series of T zeros
        if isinstance(ref_date, dict):
            return pd.Series(ref_date)

        return pd.Series(
            [ref_date] * len(sequence_pool.unique_ids),
            index=sequence_pool.unique_ids,
        )

    def _process_censoring(self, t_zeros, endpoint_dates):
        """Handle censoring and apply fallback values when needed."""
        # Align data
        aligned_data = self._align_temporal_data(t_zeros, endpoint_dates)

        # Apply censoring strategy
        if self.settings.mask_censored:
            processed_data = self._mask_missing_data(aligned_data)
        else:
            processed_data = self._apply_fallback_values(aligned_data)

        # Mark observations (using .loc to avoid warning)
        processed_data.loc[:, "observed"] = ~processed_data["end"].isna()

        return processed_data

    def _align_temporal_data(self, t_zeros, endpoint_dates):
        """Align T zeros and endpoint dates on common index."""
        common_index = t_zeros.index.intersection(endpoint_dates.index)
        start_series = t_zeros.loc[common_index]
        end_series = endpoint_dates.loc[common_index]

        return pd.DataFrame({"start": start_series, "end": end_series})

    def _mask_missing_data(self, data):
        """Remove rows with missing temporal data."""
        valid_mask = ~(data["start"].isna() | data["end"].isna())
        return data[valid_mask].copy()

    def _apply_fallback_values(self, data):
        """Apply fallback values for missing temporal data."""
        data = data.copy()  # Avoid SettingWithCopyWarning
        # Apply endpoint fallback
        if (
            data["end"].isna().any()
            and self.settings.fallback_endpoint_date is not None
        ):
            data["end"] = data["end"].fillna(self.settings.fallback_endpoint_date)

        # Apply T zero fallback
        if data["start"].isna().any():
            if self.settings.fallback_t_zero is None:
                raise ValueError(
                    "mask_censored is False but no fallback T zero is provided "
                    "and T zero is sometimes missing."
                )
            data["start"] = data["start"].fillna(self.settings.fallback_t_zero)

        return data

    def _calculate_durations(self, observation_data):
        """
        Calculate durations between start and end dates.

        Args:
            observation_data (pd.DataFrame): DataFrame with 'start' and 'end' columns.

        Returns:
            pd.Series: Series of calculated durations.
        """
        durations = calculate_duration_from_series(
            start_series=observation_data["start"],
            end_series=observation_data["end"],
            granularity=self.settings.granularity,
        )

        return durations

    def _create_survival_array(self, durations, observation_data):
        """Create a structured NumPy array for scikit-survival."""
        # Ensure consistent ordering
        sorted_data = self._sort_survival_data(observation_data, durations)

        # Build structured array
        survival_array = self._build_structured_array(
            sorted_data["observation_data"], sorted_data["durations"]
        )

        return survival_array, list(sorted_data["observation_data"].index)

    def _sort_survival_data(self, observation_data, durations):
        """Sort observation data and durations consistently."""
        observation_data = observation_data.sort_index()
        durations = durations.sort_index()
        return {"observation_data": observation_data, "durations": durations}

    def _build_structured_array(self, observation_data, durations):
        """Build the structured array for scikit-survival."""
        dtype = [("observed", bool), ("duration", float)]
        survival_array = np.zeros(len(durations), dtype=dtype)

        survival_array["observed"] = observation_data["observed"].values
        survival_array["duration"] = durations.values

        return survival_array

    def __repr__(self):
        """Return a string representation of the survival analysis."""
        return self.summarize()
