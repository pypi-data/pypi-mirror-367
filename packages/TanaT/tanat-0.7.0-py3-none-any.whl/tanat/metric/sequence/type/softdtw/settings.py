#!/usr/bin/env python3
"""
SoftDTW sequence metric settings.
"""

from typing import Union

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import viewer

from ....entity.base.metric import EntityMetric
from ...settings.base import BaseSequenceMetricSettings


@viewer
@dataclass
class SoftDTWSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for SoftDTW (Soft Dynamic Time Warping) sequence metric computation.

    Attributes:
        entity_metric:
            Specifies the metric used for calculating distances at the entity level.
            It can be either a string identifier corresponding to an EntityMetric
            in the registry (or within a working environment), such as "hamming",
            or an instance of the EntityMetric class. The default value is "hamming".

        gamma: Regularization parameter for soft-min function.
            Controls smoothness of the approximation. Lower values make it
            closer to true DTW. Must be positive. Defaults to 1.0.

        store_matrix: Whether to store the computed SoftDTW matrices.
            If True, matrices are stored in `.r_matrices` attribute.
            If False, matrices are discarded after distance computation.
            Defaults to True.

        parallel: Enable parallel computation for SequencePool operations.
            Only affects computations on sequence pools. Defaults to False.

        chunk_size: Number of sequence pairs to prepare for computation from sequence pool.
            Allows control over memory usage. Defaults to 1000.

        max_workers: Maximum number of parallel processes.
            Only relevant when parallel=True. Defaults to 4.
    """

    entity_metric: Union[str, EntityMetric] = "hamming"
    gamma: float = 1.0
    store_matrix: bool = False
