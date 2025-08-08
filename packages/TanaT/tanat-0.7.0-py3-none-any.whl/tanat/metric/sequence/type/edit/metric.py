#!/usr/bin/env python3
"""
Edit distance.
"""

import logging
import multiprocessing

from .utils import compute_edit, _process_edit_pair
from .settings import EditSequenceMetricSettings
from ...base.metric import SequenceMetric
from ....entity.base.enum import EntityMetricMode
from .....utils.misc import chunks_from_generator


LOGGER = logging.getLogger(__name__)


class EditSequenceMetric(SequenceMetric, register_name="edit"):
    """
    Edit Distance

    This similarity measure ($\\mathcal{A}$) computes the optimal matching between two sequences
    $x$ and $y$. The optimal matching is defined through matching costs, that are provided by the
    entity metric, and the deletion cost.
    It generates edit distances that are the minimal cost, in terms of insertions, deletions, and
    substitutions, for transforming one sequence into another.

    We use the Needleman-Wunsch algorithm.

    Note
    ------
    This is a purely sequential metric. The date of the events are not used.

    References
    ------------
    Levenshtein, V. (1966). Binary codes capable of correcting deletions, insertions, and
    reversals. Soviet Physics Doklady 10, 707-710

    Needleman, S. and C. Wunsch (1970). A general method applicable to the search for
    similarities in the amino acid sequence of two proteins. Journal of Molecular Biology 48,
    443-453
    """

    SETTINGS_DATACLASS = EditSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = EditSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def entity_metric(self):
        """Get the properly configured entity metric for Edit distance computation."""
        metric = self._settings.entity_metric
        metric = self._resolve_entity_metric(metric)
        return metric

    def __call__(self, seq_a, seq_b, **kwargs):
        """Calculate the Edit metric for a specific pair of sequences."""
        self._validate_sequences(seq_a=seq_a, seq_b=seq_b)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            distance = compute_edit(
                seq_a.to_numpy(),
                seq_b.to_numpy(),
                self.entity_metric.picklable_sequence_computer(
                    mode=EntityMetricMode.ALLPAIRS
                ),
                self.settings.deletion_cost,
                self.settings.as_dist,
                self.settings.norm,
            )
            return distance

    def collect(self, sequence_pool, **kwargs):
        """
        Compute Edit metric for all sequence pairs in the pool.
        Supports parallel computation when enabled in settings.
        """
        self._validate_sequence_pool(sequence_pool)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            with self._progress_bar(sequence_pool) as pbar:
                if self.settings.parallel:
                    yield from self._collect_parallel(sequence_pool, pbar)
                else:
                    yield from self._collect_serial(sequence_pool, pbar)

    def _prepare_pairs_with_arrays(self, pairs_chunk):
        """Prepare sequence pairs for processing."""
        entity_metric_seq_computer = self.entity_metric.picklable_sequence_computer(
            mode=EntityMetricMode.ALLPAIRS
        )
        prepared_pairs = []
        for pair in pairs_chunk:
            seq_a, seq_b, pair_ids = self._extract_elts_and_ids(pair)
            prepared_pairs.append(
                (
                    seq_a.to_numpy(),
                    seq_b.to_numpy(),
                    pair_ids,
                    entity_metric_seq_computer,
                    self.settings.deletion_cost,
                    self.settings.as_dist,
                    self.settings.norm,
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
                pair_ids, distance = _process_edit_pair(prepared_pair)
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
                        _process_edit_pair, prepared_pairs
                    ):
                        pbar.update(1)
                        yield pair_ids, distance
            finally:
                pool.close()
                pool.join()
