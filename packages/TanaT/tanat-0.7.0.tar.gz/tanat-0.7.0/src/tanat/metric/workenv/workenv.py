#!/usr/bin/env python3
"""
Metric working environment.
"""

from pypassist.runner.workenv.base.workenv import BaseWorkEnv
from pypassist.mixin.cachable import Cachable


class MetricWorkEnv(BaseWorkEnv, Cachable):
    """Metric work environment."""

    def __init__(self, config, parent_env=None):
        BaseWorkEnv.__init__(self, config, parent_env)
        Cachable.__init__(self)

    @Cachable.caching_property
    def entity(self):
        """The dict of instantiated event metrics."""
        return self._get_metrics("entity")

    @Cachable.caching_property
    def sequence(self):
        """The dict of instantiated sequence metrics."""
        return self._get_metrics("sequence")

    @Cachable.caching_property
    def trajectory(self):
        """The dict of instantiated trajectory metrics."""
        return self._get_metrics("trajectory")

    def _get_metrics(self, section_name):
        """
        Common internal method for retrieving dicts of instances of metrics.

        Args:
            section_name:
                The name of the section of the configuration file (e.g.
                "entity_metrics").
        """
        section = getattr(self.config, section_name)
        return {
            name: conf.get_metric(workenv=self.parent_env)
            for (name, conf) in section.items()
        }
