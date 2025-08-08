#!/usr/bin/env python3
"""
Aggregation trajectory metric settings.
"""


from typing import Union, Callable

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer import viewer

from ...settings.common import CommonTrajectoryMetricSettings


@viewer
@dataclass
class AggregationTrajectoryMetricSettings(CommonTrajectoryMetricSettings):
    """
    Configuration for aggregating metrics from sequence pairs in trajectories.

    Attributes:
        metric_mapper (MetricMapper):
            Mapping of sequence pools to their corresponding metrics.
            If not provided, a default mapping will be used.

        agg_fun (Union[str, Callable]):
            Function or string prefix for an aggregation function registered in the registry.
            Defaults to "mean".

        default_value (float):
            Value used for aggregating when a sequence is missing in one of the trajectory pairs.
            Relevant when `intersection` is False (default is `float("nan")`).

        intersection (bool):
            If True, aggregates only when all sequences are present in both trajectories.
            Defaults to False.
    """

    agg_fun: Union[str, Callable] = "mean"
    default_value: float = float("nan")
