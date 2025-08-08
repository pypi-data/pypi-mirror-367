#!/usr/bin/env python3
"""
Common base class for metrics.
"""

from abc import ABC, abstractmethod
import logging

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError
from pydantic_core import core_schema

from ..function.aggregation.base.function import AggregationFunction
from ..sequence.base.sequence import Sequence
from ..sequence.base.pool import SequencePool

LOGGER = logging.getLogger(__name__)


class Metric(ABC, Registrable, Cachable, SettingsMixin):
    """
    Base class for metrics
    """

    def __init__(self, settings, *, workenv=None):
        """
        Args:
            settings:
                The metric settings.

            workenv:
                Optional workenv instance.
        """
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)

        self._workenv = workenv

    @classmethod
    def get_metric(cls, mtype, settings=None, workenv=None):
        """
        Retrieve and instantiate a Metric.

        Args:
            mtype: Type of metric to use, resolved via type registry.
            settings: Metric-specific settings dictionary or dataclass.
            workenv: Optional working env instance.

        Returns:
            An instance of the Metric configured
            with the provided settings and workenv.
        """
        try:
            metric = cls.get_registered(mtype)(settings=settings, workenv=workenv)
        except UnregisteredTypeError as err:
            cls._unregistered_metric_error(mtype, err)

        return metric

    @classmethod
    @abstractmethod
    def _unregistered_metric_error(cls, mtype, err):
        """Raise an error for an unregistered metric with a custom message."""

    def _validate_sequence_pool(self, seqpool):
        if not isinstance(seqpool, SequencePool):
            raise ValueError(
                "Invalid sequence pool provided to the metric. "
                "Expected an instance of SequencePool. "
                f"Got {type(seqpool)}."
            )
        if hasattr(self, "_sequence_pool"):
            self._sequence_pool = (  # pylint: disable=attribute-defined-outside-init
                seqpool
            )

    def _validate_sequences(self, **sequences):
        """
        Validate multiple sequences, ensuring they are of the correct type.

        Args:
            sequences:
                Dictionary of sequences to validate.

        Raises:
            ValueError: If any sequence is invalid.
        """
        for key, sequence in sequences.items():
            if not self._is_valid_sequence(sequence):
                raise ValueError(
                    f"Invalid sequence '{key}'. Expected Sequence, got {type(sequence)}."
                )

    def _is_valid_sequence(self, sequence):
        """
        Check if a given sequence is valid.

        Args:
            sequence:
                The sequence to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return isinstance(sequence, Sequence)

    def _extract_elts_and_ids(self, pair):
        """
        Extract elements and their IDs from a pair.

        Args:
            pair:
                A tuple containing the sequence pair information.

        Returns:
            tuple: A tuple containing the elements
            (sequence_a/trajectory_a, sequence_b/trajectory_b)
            and their corresponding IDs (id_a, id_b).
        """
        elt_a = pair[0]
        elt_b = pair[1]
        pair_ids = pair[0].id_value, pair[1].id_value

        return elt_a, elt_b, pair_ids

    @Cachable.caching_method()
    def _resolve_agg_fun(self, agg_fun):
        """
        Resolve the aggregation function string identifier.
        First tries to resolve from working env if available,
        then falls back to registered functions.
        """
        if not isinstance(agg_fun, str):
            if callable(agg_fun):
                return agg_fun
            raise ValueError(
                f"Expected string identifier or callable, got {type(agg_fun).__name__}. "
                "Use a registered function name or provide a callable."
            )

        if self._workenv is not None:
            resolved = self._try_resolve_from_workenv(agg_fun)
            if resolved is not None:
                return resolved

        return self._try_resolve_from_registry(agg_fun)

    def _try_resolve_from_workenv(self, agg_fun):
        """Try to resolve aggregation function from working env."""
        LOGGER.info(
            "Attempting to resolve aggregation function '%s' from working env.", agg_fun
        )
        try:
            agg_fun_instance = self._workenv.functions.aggregation[agg_fun]
            LOGGER.info("Aggregation function '%s' resolved from working env.", agg_fun)
            return agg_fun_instance
        except KeyError:
            available = list(self._workenv.functions.aggregation.keys())
            LOGGER.info(
                "Could not resolve aggregation function '%s' from working env. Available: %s. "
                "Resolution skipped. Try from default registered functions.",
                agg_fun,
                ", ".join(available),
            )
            return None

    def _try_resolve_from_registry(self, agg_fun):
        """Try to resolve aggregation function from registry."""
        resolved_fun = AggregationFunction.get_function(agg_fun)
        LOGGER.info(
            "%s: Using aggregation function `%s` with default settings.",
            self.__class__.__name__,
            agg_fun,
        )
        return resolved_fun

    def __get_pydantic_core_schema__(self, handler):  # pylint: disable=unused-argument
        """Pydantic schema override."""
        return core_schema.any_schema()
