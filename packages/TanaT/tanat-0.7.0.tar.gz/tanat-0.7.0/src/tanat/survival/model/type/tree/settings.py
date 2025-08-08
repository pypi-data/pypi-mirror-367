#!/usr/bin/env python3
"""
Survival tree model settings.
"""

from typing import Optional, Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer

from ...base.settings import BaseSurvivalModelSettings


@viewer
@dataclass
class TreeSurvivalSettings(BaseSurvivalModelSettings):
    """
    Complete configuration for survival decision tree model.

    Combines survival array generation settings with tree-specific
    parameters for splitting criteria, depth control, and memory optimization.
    Ideal for interpretable survival analysis and non-linear relationships.

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
        splitter (str): Strategy used to split the nodes.
            - "best" → Choose the best split.
            - "random" → Choose the best random split.
        max_depth (int, optional): Maximum depth of the tree.
        min_samples_split (Union[int, float]): Minimum number of samples required
            to split an internal node.
        min_samples_leaf (Union[int, float]): Minimum number of samples required
            to be at a leaf node.
        min_weight_fraction_leaf (float): Minimum weighted fraction of the total
            sum of weights required to be at a leaf node.
        max_features (Union[int, float, str], optional): Maximum number of features
            to consider when looking for the best split.
        random_state (int, optional): Random state seed.
        max_leaf_nodes (int, optional): Grow a tree with max_leaf_nodes
            in best-first fashion.
        low_memory (bool): Use less memory and possibly be slower to apply.

    Note: static_features is inherited from BaseSurvivalModelSettings.
    granularity, mask_censored, fallback_t_zero, fallback_endpoint_date
    are inherited from SurvivalArrayGenerationSettings. query, anchor, and
    use_first are inherited from QueryDateResolverSettings.

    Examples:
        >>> # Simple interpretable tree
        >>> settings = TreeSurvivalSettings(
        ...     max_depth=5,
        ...     min_samples_split=20,
        ...     min_samples_leaf=10
        ... )

        >>> # Regularized tree with feature subsampling
        >>> settings = TreeSurvivalSettings(
        ...     max_depth=10,
        ...     max_features='sqrt',
        ...     min_samples_split=50,
        ...     random_state=42
        ... )

        >>> # Memory-efficient tree for large datasets
        >>> settings = TreeSurvivalSettings(
        ...     max_leaf_nodes=100,
        ...     low_memory=True,
        ...     splitter='random'
        ... )
    """

    splitter: str = "best"
    max_depth: Optional[int] = None
    min_samples_split: Union[int, float] = 6
    min_samples_leaf: Union[int, float] = 3
    min_weight_fraction_leaf: float = 0
    max_features: Optional[Union[int, float, str]] = None
    random_state: Optional[int] = None
    max_leaf_nodes: Optional[int] = None
    low_memory: bool = False
