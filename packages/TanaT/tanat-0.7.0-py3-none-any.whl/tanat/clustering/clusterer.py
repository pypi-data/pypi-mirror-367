#!/usr/bin/env python3
"""
Base class for clusterers.
"""

from abc import ABC, abstractmethod
import logging

import pandas as pd
from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError
from pypassist.runner.workenv.mixin.processor import ProcessorMixin

from ..sequence.base.pool import SequencePool
from ..trajectory.pool import TrajectoryPool
from ..metric.sequence.base.metric import SequenceMetric
from ..metric.trajectory.base.metric import TrajectoryMetric
from ..mixin.summarizer.clustering import ClusteringSummarizerMixin

LOGGER = logging.getLogger(__name__)


class Clusterer(
    ABC,
    Registrable,
    Cachable,
    SettingsMixin,
    ClusteringSummarizerMixin,
    ProcessorMixin,
):
    """
    Base class for clusterers.
    """

    _REGISTER = {}
    _TYPE_SUBMODULE = "type"

    def __init__(self, settings, *, workenv=None):
        """
        Initialize the clusterer with the given settings.

        Args:
            settings: Configuration settings for the clusterer.
            workenv: Optional working env instance.

        Raises:
            ValueError: If the settings type is invalid.
        """
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        ProcessorMixin.__init__(self)

        self._workenv = workenv
        self._clusters = None

    @classmethod
    def get_clusterer(cls, ctype, settings=None, workenv=None):
        """
        Retrieve and instantiate a Clusterer.

        Args:
            ctype: Type of clustering algorithm to use, resolved via type registry.
            settings: Clustering algorithm-specific settings dictionary.
            workenv: Optional working env instance.

        Returns:
            An instance of the Clusterer configured
            with the provided settings and workenv.
        """
        try:
            return cls.get_registered(ctype)(settings=settings, workenv=workenv)
        except UnregisteredTypeError as err:
            registered = cls.list_registered()
            raise UnregisteredTypeError(
                f"Unknown clusterer '{ctype}'. " f"Available clusterers: {registered}"
            ) from err

    @property
    def clusters(self):
        """
        Returns the list of cluster objects.
        """
        return self._clusters

    @abstractmethod
    def fit(self, pool):
        """
        Fit the clusterer to the given pool.
        """

    # pylint: disable=arguments-differ
    def process(self, *, pool, export, output_dir, exist_ok):
        """
        Process the clusterer in a runner.

        Args:
            pool: Pool of sequences to analyze
            export: If True, export results
            output_dir: Base output directory
            exist_ok: If True, existing output files will be overwritten

        Returns: None
        """
        self._run(pool)
        if export:
            self.export_settings(
                output_dir=output_dir,
                format_type="yaml",
                exist_ok=exist_ok,
                makedirs=True,
            )
            self._save(output_dir / "results.txt")
        return self

    def _run(self, pool):
        """
        Run the clusterer on the given pool.
        """
        self.fit(pool)

    def _save(self, output_path):
        """
        Save results to text file.
        """
        self.summarize(filename=output_path)
        LOGGER.info("Saved results to %s", output_path)

    def _validate_pool(self, pool):
        if not isinstance(pool, (SequencePool, TrajectoryPool)):
            raise ValueError(
                "Invalid pool. Expected a SequencePool or TrajectoryPool instance."
            )

    def _get_valid_metric(self, pool):
        """
        Get a valid metric from the current settings.

        Args:
            pool: The data pool (either sequence or trajectory data).

        Returns:
            Union[SequenceMetric, TrajectoryMetric]: The valid metric.
        """
        metric = self.settings.metric

        return self._resolve_metric(metric, pool)

    @Cachable.caching_method()
    def _resolve_metric(self, metric, pool):
        """
        Resolve the metric for this clusterer.
        First tries to resolve from working env if available,
        then falls back to registered metrics.

        Args:
            metric: The metric to resolve.
            pool: The sequence/trajectory pool to determine the metric type.
        Returns:
            Metric: The metric instance.
        """
        if not isinstance(metric, str):
            if isinstance(metric, (SequenceMetric, TrajectoryMetric)):
                return metric
            raise ValueError(
                f"Invalid metric: {metric}. "
                "Expected a SequenceMetric, TrajectoryMetric instance or a valid string identifier."
            )

        base_cls = (
            SequenceMetric if isinstance(pool, SequencePool) else TrajectoryMetric
        )

        if self._workenv is not None:
            resolved = self._try_resolve_metric_from_workenv(metric, base_cls)
            if resolved is not None:
                return resolved

        return self._try_resolve_metric_from_registry(metric, base_cls)

    def _try_resolve_metric_from_workenv(self, metric, base_cls):
        """Try to resolve metric from working env."""
        LOGGER.info("Attempting to resolve metric '%s' from working env.", metric)

        wenv_property = "sequence" if base_cls is SequenceMetric else "trajectory"
        metrics_dict = getattr(self._workenv.metrics, wenv_property)

        try:
            metric_inst = metrics_dict[metric]
            LOGGER.info(
                "Metric '%s' resolved from working env.",
                metric,
            )
            return metric_inst
        except KeyError:
            available = list(metrics_dict.keys())
            LOGGER.info(
                "Could not resolve %s '%s' from working env. Available: %s. "
                "Resolution skipped. Try from default registered metrics.",
                base_cls.__name__,
                metric,
                ", ".join(available),
            )
            return None

    def _try_resolve_metric_from_registry(self, mtype, base_cls):
        """Try to resolve metric from registry."""
        metric_cls = base_cls.get_metric(mtype)
        LOGGER.info(
            "%s: Using metric `%s` with default settings.",
            self.__class__.__name__,
            mtype,
        )
        return metric_cls

    def _udpate_static_pool_data(self, pool):
        """
        Update the static pool with the current clustering results.
        """
        all_clusters = []
        for cluster in self.clusters:
            item_contents = cluster.get_items()
            for item in item_contents:
                all_clusters.append((item, cluster.id))

        id_col = pool.settings.id_column
        if id_col is None:
            ## -- case of trajectory without id
            id_col = "__ID__"

        new_static_df = pd.DataFrame(
            all_clusters, columns=[id_col, self.settings.cluster_column]
        )
        pool.add_static_features(new_static_df, id_column=id_col, override=True)
