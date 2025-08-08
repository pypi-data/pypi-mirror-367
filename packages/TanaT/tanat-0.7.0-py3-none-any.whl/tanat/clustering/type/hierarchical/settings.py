#!/usr/bin/env python3
"""
Hierarchical clusterering settings.
"""

from typing import Union, Optional

from pypassist.dataclass.decorators.viewer import viewer
from pypassist.fallback.typing import Dict
from pydantic.dataclasses import dataclass, Field

from ....metric.sequence.base.metric import SequenceMetric
from ....metric.trajectory.base.metric import TrajectoryMetric


@viewer
@dataclass
class HierarchicalClustererSettings:
    """
    Configuration settings for the HierarchicalClusterer.

    Attributes:
        metric (Union[SequenceMetric, TrajectoryMetric, str]):
            The metric used for clustering. If a string identifier is is provided,
            (e.g., from a YAML configuration), it will be resolved into an `SequenceMetric`
            or `TrajectoryMetric` object from the global configuration.
        n_clusters (int):
            The number of clusters to form. Defaults to 2.
        distance_threshold (float):
            The distance threshold for clustering. If `n_clusters` is None, clustering stops
            when this threshold is reached. Defaults to None.
            If specified, `n_clusters` is ignored.
        linkage (str):
            Linkage criterion for the clustering algorithm. Options include 'complete',
            'average', etc. Defaults to 'complete'.
        model_kwargs (dict):
            Additional keyword arguments for the `AgglomerativeClustering` scikit-learn model.
            Defaults to an empty dictionary.
        cluster_column (str): The column name used to store the clustering results
            as a static feature. Defaults to "__HCLUSTERS__".
    """

    metric: Union[SequenceMetric, TrajectoryMetric, str] = "linearpairwise"
    n_clusters: int = 2
    distance_threshold: Optional[float] = None
    linkage: str = "complete"
    model_kwargs: Dict = Field(default_factory=dict)
    cluster_column: str = "__HCLUSTERS__"
