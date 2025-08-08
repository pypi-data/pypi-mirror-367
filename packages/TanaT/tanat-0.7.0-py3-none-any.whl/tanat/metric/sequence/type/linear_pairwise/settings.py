#!/usr/bin/env python3
"""
LinearPairwise sequence metric settings.
"""

from typing import Union, Callable

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import viewer

from ....entity.base.metric import EntityMetric
from ...settings.base import BaseSequenceMetricSettings


@viewer
@dataclass
class LinearPairwiseSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for computing pairwise sequence metrics between sequences.

    Attributes:
        entity_metric: Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".

        agg_fun (Union[str, Callable]):
            Function or string prefix for an aggregation function registered in the registry.
            Defaults to "mean".

        parallel: Enable parallel computation for SequencePool operations.
            Only affects computations on sequence pools. Defaults to False.

        chunk_size: Number of sequence pairs to prepare for computation from sequence pool.
            Allows control over memory usage. Defaults to 1000.

        max_workers: Maximum number of parallel processes.
            Only relevant when parallel=True. Defaults to 4.
    """

    entity_metric: Union[str, EntityMetric] = "hamming"
    agg_fun: Union[str, Callable] = "mean"
