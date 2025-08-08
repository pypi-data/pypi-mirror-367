#!/usr/bin/env python3
"""
Base settings for survival model.
"""

from datetime import datetime
from typing import Optional, Union

from pydantic.dataclasses import dataclass

from ....time.query import QueryDateResolverSettings
from ....time.granularity import Granularity


@dataclass
class SurvivalArrayGenerationSettings(QueryDateResolverSettings):
    """
    Configuration for survival array generation from temporal sequences.

    Configures how survival endpoints are identified, temporal references
    are resolved, and censoring is handled during array construction.
    Provides flexible query-based endpoint detection with fallback strategies.

    Attributes:
        query (str, optional): Query string to select endpoint occurrence in sequences.
            Can refer to any valid field (e.g. "event_type == 'hospitalization'").
        anchor (DateAnchor, optional): Reference point within intervals.
            Auto-resolved by sequence type if None:
            - EventSequence → START (events are points in time)
            - StateSequence → START (state periods start)
            - IntervalSequence → uses sequence anchor setting
        use_first (bool): If True, selects first matching row; otherwise uses last.
        granularity (Granularity): Time unit for duration calculation (days, weeks, months).
        mask_censored (bool): If True, sequences with missing dates are marked as censored.
        fallback_t_zero (datetime, optional): T zero when missing in sequence.
            Used only if mask_censored is False.
        fallback_endpoint_date (datetime, optional): Endpoint date when not found.
            Used only if mask_censored is False.
    """

    granularity: Granularity = Granularity.DAY
    mask_censored: bool = True
    fallback_t_zero: Optional[Union[float, int, datetime]] = None
    fallback_endpoint_date: Optional[Union[float, int, datetime]] = None
    # Overrides QueryDateResolverMixinSettings.query to be optional at initialization
    query: Optional[str] = None


@dataclass
class BaseSurvivalModelSettings(SurvivalArrayGenerationSettings):
    """
    Base configuration for survival analysis models.

    Combines survival array generation settings with model-specific
    feature selection capabilities. Serves as foundation for all
    survival model implementations in TanaT.

    Attributes:
        query (str, optional): Query string to select endpoint occurrence in sequences.
            Can refer to any valid field (e.g. "event_type == 'hospitalization'").
        anchor (DateAnchor, optional): Reference point within intervals.
            Auto-resolved by sequence type if None:
            - EventSequence → START (events are points in time)
            - StateSequence → START (state periods start)
            - IntervalSequence → uses sequence anchor setting
        use_first (bool): If True, selects first matching row; otherwise uses last.
        granularity (Granularity): Time unit for duration calculation (days, weeks, months).
        mask_censored (bool): If True, sequences with missing dates are marked as censored.
        fallback_t_zero (datetime, optional): T zero when missing in sequence.
            Used only if mask_censored is False.
        fallback_endpoint_date (datetime, optional): Endpoint date when not found.
            Used only if mask_censored is False.
        static_features (List[str], optional): Static features to include in model.
            If None, all available features are used.
    """

    static_features: Optional[list[str]] = None
