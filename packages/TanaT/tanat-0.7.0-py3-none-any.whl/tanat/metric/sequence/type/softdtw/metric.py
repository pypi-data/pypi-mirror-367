#!/usr/bin/env python3
"""
SoftDTW (Soft Dynamic Time Warping) metric.
"""

import logging

import multiprocessing

from .utils import compute_soft_dtw, _process_soft_dtw_pair
from .settings import SoftDTWSequenceMetricSettings
from ...base.metric import SequenceMetric
from ....entity.base.enum import EntityMetricMode
from .....utils.misc import chunks_from_generator


LOGGER = logging.getLogger(__name__)


class SoftDTWSequenceMetric(SequenceMetric, register_name="softdtw"):
    """
    Soft Dynamic Time Warping (SoftDTW)

    A differentiable version of DTW that replaces the min operator with a
    soft-minimum, allowing for gradient computation. This implementation uses
    a regularization parameter gamma to control the smoothness of the approximation.

    See Also
    --------
    DTW : DTW (Dynamic Time Warping) metric.

    References
    ----------
    .. [1] Marco Cuturi & Mathieu Blondel. "Soft-DTW: a Differentiable Loss Function for
        Time-Series", ICML 2017.
    .. [2] Mathieu Blondel, Arthur Mensch & Jean-Philippe Vert.
        "Differentiable divergences between time series",
        International Conference on Artificial Intelligence and Statistics, 2021.
    """

    SETTINGS_DATACLASS = SoftDTWSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = SoftDTWSequenceMetricSettings()

        super().__init__(settings, workenv=workenv)
        self.r_matrices = {}

    @property
    def entity_metric(self):
        """
        Get the entity metric with appropriate settings for SoftDTW computation.
        Ensures the metric is configured in ALLPAIRS mode.

        Returns:
            EntityMetric: The configured entity-level metric.

        Raises:
            ValueError: If the entity metric is not a valid EntityMetric instance.
        """
        metric = self.settings.entity_metric

        if isinstance(metric, str):
            metric = self._resolve_entity_metric(metric)

        self._validate_entity_metric(metric)
        return metric

    def __call__(self, seq_a, seq_b, **kwargs):
        """
        Calculate the SoftDTW metric for a specific pair of sequences.

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
        self._validate_sequences(seq_a=seq_a, seq_b=seq_b)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            distance, matrix = compute_soft_dtw(
                self._sequence_to_arrays(seq_a),
                self._sequence_to_arrays(seq_b),
                self.entity_metric.picklable_sequence_computer(
                    mode=EntityMetricMode.ALLPAIRS
                ),
                self.settings.gamma,
            )

            if self.r_matrices:
                self.r_matrices.clear()

            if self.settings.store_matrix:
                self.r_matrices = {(seq_a.id, seq_b.id): matrix}

            return distance

    def collect(self, sequence_pool, **kwargs):
        """
        Lazily compute and collect the metric for all pairs of sequences in the sequence pool.
        Overrides base method for optimization and parallelization purposes.

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
            if self.r_matrices:
                self.r_matrices.clear()

            with self._progress_bar(sequence_pool) as pbar:
                if self.settings.parallel:
                    yield from self._collect_parallel(sequence_pool, pbar)
                else:
                    yield from self._collect_serial(sequence_pool, pbar)

    def _sequence_to_arrays(self, sequence):
        """Convert a sequence to numpy array."""
        return sequence.to_numpy()

    def _prepare_pairs_with_arrays(self, pairs_chunk):
        """Prepare pairs for processing."""
        entity_metric_seq_computer = self.entity_metric.picklable_sequence_computer(
            mode=EntityMetricMode.ALLPAIRS
        )
        prepared_pairs = []
        for pair in pairs_chunk:
            seq_a, seq_b, pair_ids = self._extract_elts_and_ids(pair)
            prepared_pairs.append(
                (
                    self._sequence_to_arrays(seq_a),
                    self._sequence_to_arrays(seq_b),
                    pair_ids,
                    entity_metric_seq_computer,
                    self.settings.gamma,
                )
            )
        return prepared_pairs

    def _collect_serial(self, sequence_pool, pbar):
        """Process sequence pairs serially."""
        chunk_size = self.settings.chunk_size
        for pairs_chunk in chunks_from_generator(
            sequence_pool.iter_pairs(), chunk_size
        ):
            prepared_pairs = self._prepare_pairs_with_arrays(pairs_chunk)
            for prepared_pair in prepared_pairs:
                pair_ids, distance, matrix = _process_soft_dtw_pair(prepared_pair)
                if self.settings.store_matrix:
                    self.r_matrices[pair_ids] = matrix
                pbar.update(1)
                yield pair_ids, distance

    def _collect_parallel(self, sequence_pool, pbar):
        """Process sequence pairs in parallel using multiprocessing."""
        workers = self.settings.max_workers
        chunk_size = self.settings.chunk_size

        with multiprocessing.Pool(workers) as pool:
            try:
                for pairs_chunk in chunks_from_generator(
                    sequence_pool.iter_pairs(), chunk_size
                ):
                    prepared_pairs = self._prepare_pairs_with_arrays(pairs_chunk)
                    for pair_ids, distance, matrix in pool.imap(
                        _process_soft_dtw_pair, prepared_pairs
                    ):
                        if self.settings.store_matrix:
                            self.r_matrices[pair_ids] = matrix

                        pbar.update(1)
                        yield pair_ids, distance
            finally:
                pool.close()
                pool.join()
