#!/usr/bin/env python3
"""
DTW (Dynamic Time Warping) metric.
"""

import logging
import multiprocessing

from .settings import DTWSequenceMetricSettings
from .utils import compute_dtw, _process_dtw_pair
from ...base.metric import SequenceMetric
from ....entity.base.enum import EntityMetricMode
from .....utils.misc import chunks_from_generator

LOGGER = logging.getLogger(__name__)


class DTWSequenceMetric(SequenceMetric, register_name="dtw"):
    """
    DTW Distance

    Dynamic Time Warping measures similarity between two temporal sequences,
    allowing for speed variations. This implementation uses the Sakoe-Chiba
    algorithm with time constraints.

    Attributes
    ----------
    self.dtw_matrices : array-like, shape=(m + 1, n + 1) or dict of arrays-like
        Accumulated cost matrix, computed when `compute_matrix` is `True`.

    References
    ----------
    H. Sakoe, S. Chiba, Dynamic programming algorithm optimization for spoken word
    recognition, IEEE Trans. on Acoustics, Speech, and Signal Processing, 26 (1978), 43–49.
    """

    SETTINGS_DATACLASS = DTWSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = DTWSequenceMetricSettings()

        super().__init__(settings, workenv=workenv)
        self.dtw_matrices = {}

    @property
    def entity_metric(self):
        """
        Get the entity metric with appropriate settings for DTW computation.
        Ensures the metric is configured in ALLPAIRS mode.

        Returns:
            EntityMetric: The configured entity-level metric.

        Raises:
            ValueError: If the entity metric is not a valid EntityMetric instance.
        """
        metric = self.settings.entity_metric
        metric = self._resolve_entity_metric(metric)

        # if metric.settings.mode != EntityMetricMode.ALLPAIRS:
        #     with metric.with_tmp_settings(  # temporarily override settings
        #         mode=EntityMetricMode.ALLPAIRS
        #     ):
        #         LOGGER.warning(
        #             "Entity metric `%s` using mode `%s`. "
        #             "Switching to `ALLPAIRS` mode for DTW computation.",
        #             metric.__class__.__name__,
        #             metric.settings.mode.label,
        #         )
        #         return metric

        return metric

    def __call__(self, seq_a, seq_b, **kwargs):
        """
        Calculate the DTW metric for a specific pair of sequences.

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
            distance, matrix = compute_dtw(
                self._sequence_to_arrays(seq_a),
                self._sequence_to_arrays(seq_b),
                self.entity_metric.picklable_sequence_computer(
                    mode=EntityMetricMode.ALLPAIRS
                ),
                self.settings.tc_param,
                self.settings.sc_param,
                compute_matrix=self.settings.compute_matrix,
            )

            if self.dtw_matrices:
                self.dtw_matrices.clear()

            if self.settings.compute_matrix:
                self.dtw_matrices = {(seq_a.id_value, seq_b.id_value): matrix}

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

            if self.dtw_matrices:
                self.dtw_matrices.clear()

            with self._progress_bar(sequence_pool) as pbar:
                if self.settings.parallel:
                    yield from self._collect_parallel(sequence_pool, pbar)
                else:
                    yield from self._collect_serial(sequence_pool, pbar)

    def _sequence_to_arrays(self, sequence):
        """Convert a sequence to (data_array, dates_array) tuple."""
        time_cols = sequence.settings.temporal_columns()
        return (
            sequence.to_numpy(),
            sequence.to_numpy(cols=time_cols),
        )

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
                    self.settings.tc_param,
                    self.settings.sc_param,
                    self.settings.compute_matrix,
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
                pair_ids, distance, matrix = _process_dtw_pair(prepared_pair)
                if self.settings.compute_matrix:
                    self.dtw_matrices[pair_ids] = matrix
                pbar.update(1)
                yield pair_ids, distance

    def _collect_parallel(self, sequence_pool, pbar):
        """Process sequence pairs in parallel using multiprocessing."""
        workers = self.settings.max_workers
        with multiprocessing.Pool(workers) as pool:
            try:
                for pairs_chunk in chunks_from_generator(
                    sequence_pool.iter_pairs(), self.settings.chunk_size
                ):
                    prepared_pairs = self._prepare_pairs_with_arrays(pairs_chunk)
                    for pair_ids, distance, matrix in pool.imap(
                        _process_dtw_pair, prepared_pairs
                    ):
                        if self.settings.compute_matrix:
                            self.dtw_matrices[pair_ids] = matrix

                        pbar.update(1)
                        yield pair_ids, distance
            finally:
                pool.close()
                pool.join()
