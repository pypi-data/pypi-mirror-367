#!/usr/bin/env python3
"""
DTW distances settings.
"""

from typing import Union, Optional

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from pypassist.dataclass.decorators import viewer
import numpy as np

from ....entity.base.metric import EntityMetric
from ...settings.base import BaseSequenceMetricSettings


@viewer
@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class DTWSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for DTW (Dynamic Time Warping) sequence metric computation.

    Attributes:
        entity_metric: Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".

        sc_param: Sakoe-Chiba band width parameter.
            Restricts the warping path to stay within a band around the diagonal.
            Larger values allow more warping but increase computation time.
            None means no band constraint. Optional.

        tc_param: Maximum time difference allowed between compared events.
            Events separated by more than this duration are not compared.
            Expected type is np.timedelta64. None means no time constraint. Optional.

        compute_matrix: Whether to store the complete DTW matrix.
            If True, stores full distance matrix in .dtw_matrices attribute.
            If False, uses memory-efficient computation without storing matrix.
            Defaults to False.

        parallel: Enable parallel computation for SequencePool operations.
            Only affects computations on sequence pools. Defaults to False.

        chunk_size: Number of sequence pairs to prepare for computation from sequence pool.
            Allows control over memory usage. Defaults to 1000.

        max_workers: Maximum number of parallel processes.
            Only relevant when parallel=True. Defaults to 4.
    """

    entity_metric: Union[str, EntityMetric] = "hamming"
    sc_param: Optional[int] = None
    tc_param: Optional[np.timedelta64] = None
    compute_matrix: bool = False
