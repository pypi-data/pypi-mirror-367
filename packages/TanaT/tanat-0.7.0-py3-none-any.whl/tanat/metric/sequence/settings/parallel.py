#!/usr/bin/env python3
"""
Parallel settings for sequence metrics.
"""

from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass
class ParallelSettings:
    """Parallel settings for sequence metrics."""

    parallel: bool = False
    chunk_size: int = Field(default=1000, gt=0)
    max_workers: int = Field(default=4, gt=0)
