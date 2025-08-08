#!/usr/bin/env python3
"""
Longest Common Subsequence.
"""

import logging
import multiprocessing

import numpy as np

from .utils import _process_lcs_pair
from .settings import LCSSequenceMetricSettings
from ...base.metric import SequenceMetric
from .....utils.misc import chunks_from_generator


LOGGER = logging.getLogger(__name__)


class LCSSequenceMetric(SequenceMetric, register_name="lcs"):
    """
    Longest Common Subsequence

    This similarity measure ($\\mathcal{A}$) computes the length of the longest common subsequence
    (LCSS) between two sequences $x$ and $y$. Subsequences are sequences entities in a sequence
    (not necessarily contiguous). They are common when all their entities are similar pairwise.
    Two entities of the sequences are the same when they have the exact same features (whatever
    their dates).

    Note
    ------
    This is a purely sequential metric. The date of the events are not used.

    Reference
    ------------
    Elzinga, C. H. (2008). Sequence analysis: Metric representations of categorical time series.
    Sociological Methods and Research.
    """

    SETTINGS_DATACLASS = LCSSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = LCSSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    def __call__(self, seq_a, seq_b, **kwargs):
        self._validate_sequences(seq_a=seq_a, seq_b=seq_b)

        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            _, lcss, len_a, len_b = _process_lcs_pair(
                (seq_a.to_numpy(), seq_b.to_numpy(), None)
            )
            return self._compute_metric(lcss, len_a, len_b)

    def collect(self, sequence_pool, **kwargs):
        self._validate_sequence_pool(sequence_pool)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            with self._progress_bar(sequence_pool) as pbar:
                if self.settings.parallel:
                    yield from self._collect_parallel(sequence_pool, pbar)
                else:
                    yield from self._collect_serial(sequence_pool, pbar)

    def _prepare_pairs_with_arrays(self, pairs_chunk):
        return [
            (seq_a.to_numpy(), seq_b.to_numpy(), pair_ids)
            for seq_a, seq_b, pair_ids in [
                self._extract_elts_and_ids(pair) for pair in pairs_chunk
            ]
        ]

    def _collect_serial(self, sequence_pool, pbar):
        for pairs_chunk in chunks_from_generator(
            sequence_pool.iter_pairs(), self.settings.chunk_size
        ):
            prepared_pairs = self._prepare_pairs_with_arrays(pairs_chunk)
            for prepared_pair in prepared_pairs:
                pair_ids, lcss, len_a, len_b = _process_lcs_pair(prepared_pair)
                pbar.update(1)
                yield pair_ids, self._compute_metric(lcss, len_a, len_b)

    def _collect_parallel(self, sequence_pool, pbar):
        with multiprocessing.Pool(self.settings.max_workers) as pool:
            try:
                for pairs_chunk in chunks_from_generator(
                    sequence_pool.iter_pairs(), self.settings.chunk_size
                ):
                    prepared_pairs = self._prepare_pairs_with_arrays(pairs_chunk)
                    for pair_ids, lcss, len_a, len_b in pool.imap(
                        _process_lcs_pair, prepared_pairs
                    ):
                        pbar.update(1)
                        yield pair_ids, self._compute_metric(lcss, len_a, len_b)
            finally:
                pool.close()
                pool.join()

    def _compute_metric(self, lcss_length, len_a, len_b):
        if self.settings.as_dist:
            if self.settings.norm:
                return 1.0 - float(lcss_length) / np.sqrt(len_a * len_b)
            return float(len_a + len_b - 2 * lcss_length)
        return float(lcss_length)
