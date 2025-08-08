#!/usr/bin/env python3
"""
Picklable helpers.
"""

import dataclasses


class _EntityMetricPicklableComputer:
    """
    A picklable wrapper to compute entity metric distances between sequences.

    This class is designed to encapsulate entity metric computations in a way
    that can be serialized for parallel processing.
    """

    def __init__(self, compute_func, settings):
        self.compute_func = compute_func
        self.settings = settings

    def __call__(self, arrays_a, arrays_b):
        return self.compute_func(arrays_a, arrays_b, self.settings)

    @classmethod
    def from_entity_metric(cls, entity_metric, **kwargs):
        """Create a picklable wrapper from an EntityMetric instance."""
        settings = entity_metric.settings
        if kwargs:
            settings = dataclasses.replace(entity_metric.settings, **kwargs)
        # pylint: disable=protected-access
        return cls(entity_metric._compute_sequence_array, settings)
