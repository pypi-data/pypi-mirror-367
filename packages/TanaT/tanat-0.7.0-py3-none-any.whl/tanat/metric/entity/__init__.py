#!/usr/bin/env python3
"""Entity metric package."""

# Hamming
from .type.hamming.metric import HammingEntityMetric
from .type.hamming.settings import HammingEntityMetricSettings

__all__ = [
    "HammingEntityMetric",
    "HammingEntityMetricSettings",
]
