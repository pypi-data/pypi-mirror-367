#!/usr/bin/env python3
"""
Coxnet survival model settings.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.fallback.typing import List
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ...base.settings import BaseSurvivalModelSettings


@viewer
@dataclass
class CoxnetSurvivalSettings(BaseSurvivalModelSettings):
    """
    Complete configuration for Cox proportional hazards model with elastic net regularization.

    Combines survival array generation settings with Cox regression specific
    parameters including regularization, normalization, and solver configuration.
    Optimized for high-dimensional survival analysis with feature selection.

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
        n_alphas (int): Number of values to test for the regularization parameter alpha.
        alphas (List[int], optional): Override the default values of alpha to be tested.
        alpha_min_ratio (Union[float, "auto"]): If "auto", set the minimum value
            of alpha to 1e-4 times the maximum of the default values. If a float,
            set the minimum value of alpha to `alpha_min_ratio` times the maximum
            of the default values.
        l1_ratio (float): Mixing parameter for the elastic net penalty.
        penalty_factor (float, optional): Rescale the penalty term by multiplying it with
            this factor. By default, penalty_factor is set to 1.0.
        normalize (bool): If True, the features will be standardized before fitting the model.
        tol (float): Convergence tolerance for the coordinate descent solver.
        max_iter (int): Maximum number of iterations of the coordinate descent solver.
        verbose (bool): Whether to print progress messages.

    Note: static_features is inherited from BaseSurvivalModelSettings.
    granularity, mask_censored, fallback_t_zero, fallback_endpoint_date
    are inherited from SurvivalArrayGenerationSettings. query, anchor, and
    use_first are inherited from QueryDateResolverSettings.

    Examples:
        >>> # Basic Cox model with default regularization
        >>> settings = CoxnetSurvivalSettings()

        >>> # High regularization for feature selection
        >>> settings = CoxnetSurvivalSettings(
        ...     l1_ratio=0.9,  # More L1 penalty for sparsity
        ...     n_alphas=200,  # More alpha values to test
        ...     normalize=True  # Standardize features
        ... )

        >>> # Custom alpha grid with early stopping
        >>> settings = CoxnetSurvivalSettings(
        ...     alphas=[0.001, 0.01, 0.1, 1.0],
        ...     tol=1e-6,
        ...     max_iter=50000
        ... )
    """

    n_alphas: int = 100
    alphas: Optional[List[int]] = None
    alpha_min_ratio: Union[float, str] = "auto"
    l1_ratio: float = 0.5
    penalty_factor: Optional[float] = None
    normalize: bool = False
    tol: float = 1e-7
    max_iter: int = 100000
    verbose: bool = False
