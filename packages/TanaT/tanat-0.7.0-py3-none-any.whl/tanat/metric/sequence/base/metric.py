#!/usr/bin/env python3
"""
Base class for sequence metrics.
"""

from abc import abstractmethod
import logging

import numpy as np
import pandas as pd
from tqdm import tqdm
from pypassist.utils.export import export_to_csv
from pypassist.mixin.cachable import Cachable
from pypassist.runner.workenv.mixin.processor import ProcessorMixin


from .exception import UnregisteredSequenceMetricTypeError
from ...base import Metric
from ...entity.base.metric import EntityMetric

LOGGER = logging.getLogger(__name__)


class SequenceMetric(Metric, ProcessorMixin):
    """
    Base class for sequence metrics.
    """

    _REGISTER = {}

    def __init__(self, settings, *, workenv=None):
        """
        Args:
            settings:
                The metric settings.

            workenv:
                Optional workenv instance.
        """
        Metric.__init__(self, settings, workenv=workenv)
        ProcessorMixin.__init__(self)

    @abstractmethod
    def __call__(self, seq_a, seq_b, **kwargs):
        """
        Calculate the metric for a specific pair of sequences.

        Args:
            seq_a (Sequence):
                First sequence.
            seq_b (Sequence):
                Second sequence.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            float: The metric value for the sequence pair.
        """

    def collect_as_matrix(
        self,
        sequence_pool,
        *,
        missing_value=np.nan,
        sparse=False,
        **kwargs,
    ):
        """
        Generate a collection matrix from the metric results.

        Args:
            sequence_pool (SequencePool):
                Pool of Sequences to collect metrics from.
            missing_value (float):
                The value to use for missing values in the matrix.
                Defaults to np.nan.
            sparse (bool):
                If True, return a sparse matrix without filling the lower part and missing values.
                Defaults to False.
            kwargs (Optional[Any]):
                Additional settings that override the default configuration.

        Returns:
            pd.DataFrame: DataFrame containing the matrix of metric results
            for the trajectory pairs.
        """
        collection = self.collect_as_dict(sequence_pool, **kwargs)
        df_pairs = pd.DataFrame(collection.items(), columns=["pair", "value"])
        df_pairs[["id_a", "id_b"]] = df_pairs["pair"].tolist()

        matrix_df = df_pairs.pivot(index="id_a", columns="id_b", values="value")
        matrix_df.index.name = None

        if not sparse:
            matrix_df = matrix_df.combine_first(matrix_df.T)
            matrix_df.fillna(float(missing_value), inplace=True)
        return matrix_df

    @Cachable.caching_method()
    def collect_as_dict(self, sequence_pool, **kwargs):
        """
        Compute and collect the metric for all pairs of sequences in the sequence pool.

        Args:
            sequence_pool (SequencePool):
                The sequence pool containing sequences.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            dict: Metric results for each pair of sequences.
        """
        return dict(self.collect(sequence_pool, **kwargs))

    def collect(self, sequence_pool, **kwargs):
        """
        Lazily compute and collect the metric for all pairs of sequences in the sequence pool.

        Args:
            sequence_pool (SequencePool):
                The sequence pool containing sequences.
            kwargs:
                Optional arguments to override specific settings.

        Yields:
            tuple: Pair of sequence IDs and their computed metric.
        """
        self._validate_sequence_pool(sequence_pool)

        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            # -- Compute the metric for all pairs of sequences
            for pair in sequence_pool.iter_pairs():
                seq_a, seq_b, pair_ids = self._extract_elts_and_ids(pair)
                yield pair_ids, self(seq_a, seq_b)

    @Cachable.caching_method()
    def _resolve_entity_metric(self, metric):
        """
        Resolve the entity metric for this metric.
        First tries to resolve from working env if available,
        then falls back to registered metrics.

        Args:
            metric: The entity metric to resolve.
        Returns:
            Metric: The entity metric instance.
        """
        if not isinstance(metric, str):
            self._validate_entity_metric(metric)
            return metric

        if self._workenv is not None:
            resolved = self._try_resolve_entity_metric_from_workenv(metric)
            if resolved is not None:
                return resolved

        return self._try_resolve_entity_metric_from_registry(metric)

    def _try_resolve_entity_metric_from_workenv(self, metric):
        """Try to resolve entity metric from working env."""
        LOGGER.info(
            "Attempting to resolve entity metric '%s' from working env.", metric
        )
        try:
            entity_metric = self._workenv.metrics.entity[metric]
            LOGGER.info("Entity metric '%s' resolved from working env.", metric)
            return entity_metric
        except KeyError:
            available = list(self._workenv.metrics.entity.keys())
            LOGGER.info(
                "Could not resolve entity metric '%s' from working env. Available: %s. "
                "Resolution skipped. Try from default registered metrics",
                metric,
                ", ".join(available),
            )
            return None

    def _try_resolve_entity_metric_from_registry(self, mtype):
        """Try to resolve entity metric from registry."""
        resolved_metric = EntityMetric.get_metric(mtype)
        LOGGER.info(
            "%s: Using entity metric `%s` with default settings.",
            self.__class__.__name__,
            mtype,
        )
        return resolved_metric

    def _validate_entity_metric(self, metric):
        if not isinstance(metric, EntityMetric):
            raise ValueError(
                f"Invalid entity metric: {metric}. "
                "Expected a EntityMetric instance or a valid string identifier."
            )

    def _progress_bar(self, sequence_pool):
        """Create a progress bar for sequence pool computation.

        Args:
            sequence_pool (SequencePool): Pool of sequences to process.

        Returns:
            tqdm: Configured progress bar instance.
        """
        n_sequences = len(sequence_pool)
        total_pairs = (n_sequences * (n_sequences - 1)) // 2
        desc = (
            f"Computing {self.__class__.__name__} ({self.settings.max_workers} workers)"
            if self.settings.parallel
            else f"Computing {self.__class__.__name__}"
        )
        return tqdm(total=total_pairs, desc=desc)

    # pylint: disable=arguments-differ
    def process(self, *, sequence_pool, export, output_dir, exist_ok):
        """
        Compute metric in a runner.

        Args:
            sequence_pool: Pool of sequences to analyze
            export: If True, export results
            output_dir: Base output directory
            exist_ok: If True, existing output files will be overwritten

        Returns:
            DataFrame with metric results matrix
        """
        matx_res = self.collect_as_matrix(sequence_pool)
        if export:
            self.export_settings(
                output_dir=output_dir,
                format_type="yaml",
                exist_ok=exist_ok,
                makedirs=True,
            )
            export_to_csv(matx_res, output_dir / "results.csv")
        return matx_res

    @classmethod
    def _unregistered_metric_error(cls, mtype, err):
        """Raise an error for an unregistered sequence metric with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredSequenceMetricTypeError(
            f"Unknown sequence metric: '{mtype}'. " f"Available metrics: {registered}"
        ) from err
