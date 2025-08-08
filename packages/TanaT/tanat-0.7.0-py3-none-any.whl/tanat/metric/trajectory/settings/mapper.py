#!/usr/bin/env python3
"""
Mapping between seqpool and sequence metric.
"""

from typing import Union, Optional

from pydantic.dataclasses import dataclass
from pypassist.fallback.typing import Dict
from pypassist.dataclass.decorators.viewer import viewer

from ...sequence.base.metric import SequenceMetric


@viewer
@dataclass
class MetricMapper:
    """Map sequence pools to metrics.

    Links pools to metrics using either string identifiers for registered metrics
    or custom metric instances.

    Attributes:
        pool_metrics: Maps pool ids to Sequence metrics.
            key: A string identifier (e.g. "pool1")
            value: A string identifier (e.g. "linearpairwise") or SequenceMetric
                instance.
        default_metric:
            Fallback SequenceMetric identifier if no pool_metrics specified.
            (Default: "linearpairwise")

    Example:
        ```python
        mapper = MetricMapper(
            pool_metrics={
                "pool1": "linearpairwise",
                "pool2": "linearpairwise",
            },
        )
        ```
    """

    pool_metrics: Optional[Dict[str, Union[str, SequenceMetric]]] = None
    default_metric: str = "linearpairwise"

    def __init__(self, **pool_metrics):
        self.pool_metrics = None
        if pool_metrics:
            self.pool_metrics = dict(pool_metrics)

        self.__post_init__()

    def __post_init__(self):
        if self.pool_metrics is None:
            self.pool_metrics = {}

    def get_metric_for_pool(self, pool_name):
        """
        Get the metric for a given sequence pool.
        If no metric was specified, creates a default LinearPairwiseSequenceMetric.
        """
        if pool_name not in self.pool_metrics:
            self.pool_metrics[pool_name] = self.default_metric

        metric = self.pool_metrics[pool_name]

        return self._resolve_sequence_metric(metric)

    def _resolve_sequence_metric(self, metric):
        """
        Resolve the sequence metric for this mapper.

        Args:
            metric:
                the sequence metric to resolve.

        Returns:
            Metric: The metric instance.

        Raises:
            ValueError: If the metric is not a valid SequenceMetric instance.
        """
        if isinstance(metric, SequenceMetric):
            return metric

        if isinstance(metric, str):
            return SequenceMetric.get_metric(metric)

        raise ValueError(
            f"Invalid metric: {metric}. "
            "Expected a SequenceMetric instance or a valid string identifier."
        )
