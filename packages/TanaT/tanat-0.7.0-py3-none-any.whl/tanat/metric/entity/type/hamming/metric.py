# #!/usr/bin/env python3
"""
Hamming Entity metric.
"""

import numpy as np

from .utils import (
    compute_hamming_elementwise,
    compute_hamming_allpairs,
    pad_to_length,
    get_cost_from_dict,
)
from .settings import HammingEntityMetricSettings
from ...base.metric import EntityMetric
from ...base.enum import EntityMetricMode
from .....loader.base import Loader


class HammingEntityMetric(EntityMetric, register_name="hamming"):
    """
    Hamming Entity metric.
    """

    SETTINGS_DATACLASS = HammingEntityMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = HammingEntityMetricSettings()

        super().__init__(settings, workenv=workenv)

    @property
    def cost_dict(self):
        """Return validated cost dictionary from settings."""
        if self._settings.cost is None:
            return None

        cost_dict = self._settings.cost
        if isinstance(cost_dict, Loader):
            cost_dict = self._settings.cost.load()

        if isinstance(cost_dict, str):
            cost_dict = self._try_resolve_loader_from_workenv(cost_dict)

        if not isinstance(cost_dict, dict):
            raise ValueError(
                "Field `cost` must be a dictionary, a Loader instance, "
                "or a string referencing a Loader in the workenv. "
                f"Got: {type(cost_dict)}"
            )
        return self._settings.cost

    def __call__(self, ent_a, ent_b, **kwargs):
        """
        Compute the metric for a specific pair of entities.

        Args:
            ent_a (Entity):
                First sequence.

            ent_b (Entity):
                Second sequence.

            kwargs:
                Optional arguments to override specific settings.

        Returns:
            float: The metric value for the entity pair.
        """
        self._validate_entities(ent_a=ent_a, ent_b=ent_b)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            if self.cost_dict is not None:
                return self.cost_dict.get(
                    (ent_a.value, ent_b.value), self._settings.default_value
                )

            return float(ent_a.value != ent_b.value)

    def compute_sequence(self, seq_a, seq_b, **kwargs):
        """
        Compute the EntityMetric between two sequences.
        Overrides the base `compute_sequence` method for optimization purposes.

        Args:
            seq_a (Sequence):
                First sequence.

            seq_b (Sequence):
                Second sequence.

            kwargs:
                Optional arguments to override specific settings.

        Returns:
            np.ndarray: An array of entity metric values.
        """
        self._validate_sequences(seq_a=seq_a, seq_b=seq_b)
        with self.with_tmp_settings(**kwargs):  # temporarily override settings
            arrays_a = seq_a.to_numpy()
            arrays_b = seq_b.to_numpy()

            return self._compute_sequence_array(arrays_a, arrays_b, self._settings)

    @staticmethod
    def _compute_sequence_array(arrays_a, arrays_b, settings):
        """
        Compute Hamming distance between two sequences of arrays.

        Args:
            arrays_a: First sequence array
            arrays_b: Second sequence array
            settings: Configuration settings for the computation

        Returns:
            Array of distances (elementwise) or distance matrix (allpairs)
        """
        compute_func = (
            HammingEntityMetric._compute_elementwise_distance
            if settings.mode == EntityMetricMode.ELEMENTWISE
            else HammingEntityMetric._compute_allpairs_distance
        )

        return compute_func(arrays_a, arrays_b, settings)

    @staticmethod
    def _compute_elementwise_with_cost(arrays_a, arrays_b, cost_dict, default_value):
        """Compute elementwise distances using cost dictionary."""
        return np.array(
            [
                get_cost_from_dict(a[0], b[0], cost_dict, default_value)
                for a, b in zip(arrays_a, arrays_b)
            ]
        )

    @staticmethod
    def _compute_allpairs_with_cost(arrays_a, arrays_b, cost_dict, default_value):
        """Compute all-pairs distances using cost dictionary."""
        n, m = len(arrays_a), len(arrays_b)
        result = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                result[i, j] = get_cost_from_dict(
                    arrays_a[i][0], arrays_b[j][0], cost_dict, default_value
                )
        return result

    @staticmethod
    def _compute_elementwise_distance(arrays_a, arrays_b, settings):
        """Compute elementwise distances with trimming and padding."""
        min_length = min(len(arrays_a), len(arrays_b))
        arrays_a_trim = arrays_a[:min_length]
        arrays_b_trim = arrays_b[:min_length]

        result = (
            compute_hamming_elementwise(arrays_a_trim, arrays_b_trim)
            if settings.cost is None
            else HammingEntityMetric._compute_elementwise_with_cost(
                arrays_a_trim, arrays_b_trim, settings.cost, settings.default_value
            )
        )

        if settings.pad_output:
            max_length = max(len(arrays_a), len(arrays_b))
            result = pad_to_length(result, max_length, settings.default_value)

        return result

    @staticmethod
    def _compute_allpairs_distance(arrays_a, arrays_b, settings):
        """Compute all-pairs distances."""
        return (
            compute_hamming_allpairs(arrays_a, arrays_b)
            if settings.cost is None
            else HammingEntityMetric._compute_allpairs_with_cost(
                arrays_a, arrays_b, settings.cost, settings.default_value
            )
        )

    def _try_resolve_loader_from_workenv(self, loader):
        """Try to resolve loader from working env."""
        loader = self._workenv.loaders.get(loader, None)
        if loader is None:
            available = list(self._workenv.loaders.keys())
            raise ValueError(
                f"Could not resolve loader '{loader}' from working env. ",
                f"Available: {available}. ",
            )

        return loader
