#!/usr/bin/env python3
"""
Base settings for sequence metrics.
"""

from pydantic.dataclasses import dataclass

from .parallel import ParallelSettings


@dataclass
class BaseSequenceMetricSettings(ParallelSettings):
    """
    Base class for sequence metric settings.
    """
