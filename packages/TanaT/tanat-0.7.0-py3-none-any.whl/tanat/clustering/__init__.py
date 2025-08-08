#!/usr/bin/env python3
"""Clustering package."""

## -- hierarchical
from .type.hierarchical.clusterer import HierarchicalClusterer
from .type.hierarchical.settings import HierarchicalClustererSettings

__all__ = [
    "HierarchicalClusterer",
    "HierarchicalClustererSettings",
]
