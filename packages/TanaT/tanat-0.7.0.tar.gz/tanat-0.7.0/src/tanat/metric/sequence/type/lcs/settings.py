#!/usr/bin/env python3
"""
Longest Common Subsequence settings.
"""

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import viewer

from ...settings.base import BaseSequenceMetricSettings


@viewer
@dataclass
class LCSSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for LCS sequence metric computation.

    Attributes:
        as_dist: If True, returns a distance measure. If False (default),
            returns the LCS length.

        norm: Normalizes the distance (only when as_dist is True).

        parallel: Enable parallel computation for SequencePool operations.
            Only affects computations on sequence pools. Defaults to False.

        chunk_size: Number of sequence pairs to prepare for computation from sequence pool.
            Allows control over memory usage. Defaults to 1000.

        max_workers: Maximum number of parallel processes.
            Only relevant when parallel=True. Defaults to 4.
    """

    as_dist: bool = False
    norm: bool = False
