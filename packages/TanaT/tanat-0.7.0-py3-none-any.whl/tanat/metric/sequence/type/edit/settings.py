#!/usr/bin/env python3
"""
Edit distance settings.
"""

from typing import Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import viewer

from ....entity.base.metric import EntityMetric
from ...settings.base import BaseSequenceMetricSettings


@viewer
@dataclass
class EditSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for Edit Distance sequence metric computation.

    Attributes:
        entity_metric: Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".

        deletion_cost: Cost for deletion/insertion operations.
            Can be a float (same cost for all entities) or a callable that computes
            the cost based on entity features. Defaults to 1.0.

        as_dist: If True, returns distance measure. If False, returns similarity.
            Defaults to False.

        norm: Whether to normalize the distance score.
            Only applies when as_dist=True. Defaults to False.

        parallel: Enable parallel computation for SequencePool operations.
            Only affects computations on sequence pools. Defaults to False.

        chunk_size: Number of sequence pairs to prepare for computation from sequence pool.
            Allows control over memory usage. Defaults to 1000.

        max_workers: Maximum number of parallel processes.
            Only relevant when parallel=True. Defaults to 4.
    """

    entity_metric: Union[str, EntityMetric] = "hamming"
    deletion_cost: float = 1.0
    as_dist: bool = False
    norm: bool = False
