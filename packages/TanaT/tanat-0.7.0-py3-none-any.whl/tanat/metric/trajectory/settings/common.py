#!/usr/bin/env python3
"""
Common settings for trajectory metrics.
"""


import dataclasses

from pypassist.mixin.settings import create_settings_snapshot

from .mapper import MetricMapper


@dataclasses.dataclass
class CommonTrajectoryMetricSettings:
    """
    Common settings for trajectory metrics.
    """

    metric_mapper: MetricMapper = dataclasses.field(default_factory=MetricMapper)
    intersection: bool = False

    def __post_init__(self):
        # Convert dict to MetricMapper if needed
        if isinstance(self.metric_mapper, dict):
            # pylint: disable=not-a-mapping
            self.metric_mapper = MetricMapper(**self.metric_mapper)

    def __snapshot_metric_mapper__(self):
        """
        Custom snapshot for the `metric_mapper` field.

        Handles non-copyable (cacheable) objects by extracting their settings.

        Used to detect changes and trigger cache invalidation.
        """
        metric_mapper = self.metric_mapper
        snapshot = {}
        for pool_name, metric in metric_mapper.pool_metrics.items():
            if hasattr(metric, "is_cachable"):  # Handle non-copyable objects
                settings = getattr(metric, "settings", None)
                settings_snapshot = create_settings_snapshot(settings)
                snapshot[pool_name] = settings_snapshot
                continue

            # should be a string identifier to resolve
            snapshot[pool_name] = metric
        return snapshot
