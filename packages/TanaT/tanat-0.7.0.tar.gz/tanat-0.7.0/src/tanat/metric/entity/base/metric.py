#!/usr/bin/env python3
"""
Base class for registable event metrics.
"""

from abc import abstractmethod

from .exception import UnregisteredEntityMetricTypeError
from .picklable import _EntityMetricPicklableComputer
from ....sequence.base.entity import Entity
from ...base import Metric


class EntityMetric(Metric):
    """
    Base class for event metrics.
    """

    _REGISTER = {}

    @abstractmethod
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

    def compute_sequence(self, seq_a, seq_b, **kwargs):
        """
        Compute the EntityMetric between two sequences.

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
            data_a = seq_a.entities()
            data_b = seq_b.entities()
            yield from map(lambda ent_pair: self(*ent_pair), zip(data_a, data_b))

    def picklable_sequence_computer(self, **kwargs):
        """
        Return a picklable computer for parallel sequence metric computation.

        Returns a callable object that encapsulates the core computation logic
        (_compute_sequence_array) and settings in a way that can be serialized
        for parallel processing with multiprocessing.Pool.

        Args:
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            _EntityMetricPicklableComputer: Picklable wrapper for sequence computation

        Note:
            This is the recommended way to use entity metrics in parallel computations,
            as it properly handles serialization of the computation logic and settings.
        """
        return _EntityMetricPicklableComputer.from_entity_metric(self, **kwargs)

    @staticmethod
    @abstractmethod
    def _compute_sequence_array(arrays_a, arrays_b, settings):
        """
        Compute EntityMetric between two sequences of arrays.

        Args:
            arrays_a: First sequence array
            arrays_b: Second sequence array
            settings: Configuration settings for the computation

        Returns:
            Array of distances (elementwise) or distance matrix (allpairs)
        """

    def _validate_entities(self, **entities):
        """
        Validate multiple sequences, ensuring they are of the correct type.

        Args:
            entities:
                Dictionary of entities to validate.

        Raises:
            ValueError: If any entity is invalid.
        """
        for key, entity in entities.items():
            if not self._is_valid_entity(entity):
                raise ValueError(
                    f"Invalid sequence '{key}'. Expected Entity, got {type(entity)}."
                )

    def _is_valid_entity(self, entity):
        """
        Check if a given sequence is valid.

        Args:
            entity:
                The entity to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return isinstance(entity, Entity)

    @classmethod
    def _unregistered_metric_error(cls, mtype, err):
        """Raise an error for an unregistered entity metric with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredEntityMetricTypeError(
            f"Unknown entity metric: '{mtype}'. " f"Available metrics: {registered}"
        ) from err
