#!/usr/bin/env python3
"""
LinearPairwise sequence metric.
"""

import logging
import multiprocessing

from .utils import _process_linear_pair
from .settings import LinearPairwiseSequenceMetricSettings
from ...base.metric import SequenceMetric
from ....entity.base.enum import EntityMetricMode
from .....utils.misc import chunks_from_generator


LOGGER = logging.getLogger(__name__)


class LinearPairwiseSequenceMetric(SequenceMetric, register_name="linearpairwise"):
    """
    Linear pairwise sequence metric.
    """

    SETTINGS_DATACLASS = LinearPairwiseSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = LinearPairwiseSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def entity_metric(self):
        """
        Get the entity metric with appropriate settings for linear pairwise computation.
        Ensures the metric is configured in `ELEMENTWISE` mode.

        Returns:
            EntityMetric: The configured entity-level metric.
        """
        metric = self._settings.entity_metric
        metric = self._resolve_entity_metric(metric)
        return metric

    @property
    def agg_fun(self):
        """
        Retrieves the aggregation function.
        """
        agg_fun = self._settings.agg_fun
        return self._resolve_agg_fun(agg_fun)

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
            float: The aggregated metric value for the sequence pair.
        """
        self._validate_sequences(seq_a=seq_a, seq_b=seq_b)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            agg_fun = self.agg_fun
            return agg_fun(
                self.entity_metric.compute_sequence(
                    seq_a, seq_b, mode=EntityMetricMode.ELEMENTWISE
                )
            )

    def collect(self, sequence_pool, **kwargs):
        """Lazily compute and collect the metric for all pairs of sequences."""
        self._validate_sequence_pool(sequence_pool)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            with self._progress_bar(sequence_pool) as pbar:
                if self.settings.parallel:
                    yield from self._collect_parallel(sequence_pool, pbar)
                else:
                    yield from self._collect_serial(sequence_pool, pbar)

    def _prepare_pairs_with_arrays(self, pairs_chunk):
        """Prepare pairs for processing."""
        entity_metric_seq_computer = self.entity_metric.picklable_sequence_computer(
            mode=EntityMetricMode.ELEMENTWISE
        )
        agg_fun = self.agg_fun
        prepared_pairs = []

        for pair in pairs_chunk:
            seq_a, seq_b, pair_ids = self._extract_elts_and_ids(pair)
            prepared_pairs.append(
                (
                    seq_a.to_numpy(),
                    seq_b.to_numpy(),
                    pair_ids,
                    entity_metric_seq_computer,
                    agg_fun,
                )
            )
        return prepared_pairs

    def _collect_serial(self, sequence_pool, pbar):
        """Process sequence pairs serially."""
        for pairs_chunk in chunks_from_generator(
            sequence_pool.iter_pairs(), self.settings.chunk_size
        ):
            prepared_pairs = self._prepare_pairs_with_arrays(pairs_chunk)
            for prepared_pair in prepared_pairs:
                pair_ids, distance = _process_linear_pair(prepared_pair)
                pbar.update(1)
                yield pair_ids, distance

    def _collect_parallel(self, sequence_pool, pbar):
        """Process sequence pairs in parallel using multiprocessing."""
        with multiprocessing.Pool(self.settings.max_workers) as pool:
            try:
                for pairs_chunk in chunks_from_generator(
                    sequence_pool.iter_pairs(), self.settings.chunk_size
                ):
                    prepared_pairs = self._prepare_pairs_with_arrays(pairs_chunk)
                    for pair_ids, distance in pool.imap(
                        _process_linear_pair, prepared_pairs
                    ):
                        pbar.update(1)
                        yield pair_ids, distance
            finally:
                pool.close()
                pool.join()
