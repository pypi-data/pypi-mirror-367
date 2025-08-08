#!/usr/bin/env python3
"""
Hierarchical clusterer.
"""

import logging

from sklearn.cluster import AgglomerativeClustering
from pypassist.mixin.cachable import Cachable

from ...clusterer import Clusterer
from ...cluster import Cluster
from .settings import HierarchicalClustererSettings


LOGGER = logging.getLogger(__name__)


class HierarchicalClusterer(Clusterer, register_name="hierarchical"):
    """
    Hierarchical clustering implementation using AgglomerativeClustering.
    """

    SETTINGS_DATACLASS = HierarchicalClustererSettings

    def __init__(self, settings=None, *, workenv=None):
        """
        Initialize the hierarchical clusterer with the given settings.

        Args:
            settings: Configuration settings for the hierarchical clusterer.
            If None, default HierarchicalClustererSettings will be used.
            workenv: Optional working env instance.

        Raises:
            ValueError: If the settings type is invalid.
        """
        if settings is None:
            settings = HierarchicalClustererSettings()

        super().__init__(settings, workenv=workenv)
        self._model = None

    @property
    def model(self):
        """
        Returns an instance of AgglomerativeClustering configured with precomputed metrics
        and the current settings.

        Returns:
            AgglomerativeClustering: The configured classifier.
        """

        if self._model is None:
            self._model = self._init_model()

        return self._model

    def _init_model(self):
        """
        Initializes the clustering model with the current settings.
        """
        forbidden_kwargs = ["metric", "n_clusters", "linkage", "distance_threshold"]
        for kwarg in forbidden_kwargs:
            if kwarg in self.settings.model_kwargs:
                LOGGER.warning(
                    "Invalid argument `%s` provided in model_kwargs. It will be ignored.",
                    kwarg,
                )
                self.settings.model_kwargs.pop(kwarg)

        if self.settings.distance_threshold is not None:
            n_clusters = None
        else:
            n_clusters = self.settings.n_clusters

        return AgglomerativeClustering(
            metric="precomputed",
            n_clusters=n_clusters,
            linkage=self.settings.linkage,
            distance_threshold=self.settings.distance_threshold,
            **self.settings.model_kwargs,
        )

    def fit(self, pool, **kwargs):
        """
        Fits the clustering model to the provided data pool.

        Args:
            pool: The data pool (either sequence or trajectory data).
            kwargs: Optional overrides for specific settings.

        Returns:
            self: The fitted clusterer. Allows chaining.
        """
        self._validate_pool(pool)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            metric = self._get_valid_metric(pool)
            self._compute_fit(metric, pool, self.model)
            self._udpate_static_pool_data(pool)
        return self

    @Cachable.caching_method()
    def _compute_fit(self, metric, pool, model):
        """
        Computes and applies the clustering model to the data.

        Args:
            metric: The metric to compute distances between data points.
            pool: The data pool (sequence or trajectory data).
            model: The clustering model to use.
        """
        dist_matrix = metric.collect_as_matrix(pool)
        self._model = model.fit(dist_matrix)
        self._create_clusters(self._model.labels_, dist_matrix)

    def _create_clusters(self, labels, metric_data):
        """
        Creates clusters based on the predicted labels.

        Args:
            labels (List[int]): The predicted cluster labels.
            metric_data (pd.DataFrame): The distance matrix or metric data.

        Returns:
            List[Cluster]: A list of created `Cluster` objects.
        """
        item_ids = self._extract_item_ids(metric_data)
        clusters = {}

        for idx, cluster_id in enumerate(labels):
            item_id = item_ids[idx]
            if cluster_id not in clusters:
                clusters[cluster_id] = Cluster(cluster_id)
            clusters[cluster_id].add_item(item_id)
        self._clusters = list(clusters.values())

    def _extract_item_ids(self, metric_data):
        """
        Extracts unique item IDs from the metric data.

        Args:
            metric_data (pd.DataFrame): The data containing the metric results.

        Returns:
            List[str]: A list of unique item IDs.
        """
        return list(metric_data.columns)
