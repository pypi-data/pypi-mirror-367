#!/usr/bin/env python3
"""
Tanat working environment.
"""

from pypassist.runner.workenv.base.workenv import BaseWorkEnv
from pypassist.mixin.cachable import Cachable

from ...metric.workenv.workenv import MetricWorkEnv

# from ...visualization.workenv.workenv import VisualizationWorkEnv
from ...function.workenv.workenv import FunctionWorkEnv


class TanatWorkEnv(BaseWorkEnv, Cachable):
    """Tanat work environment."""

    def __init__(self, config, parent_env=None):
        BaseWorkEnv.__init__(self, config, parent_env)
        Cachable.__init__(self)

    @Cachable.caching_property
    def sequence_pools(self):
        """The dict of instantiated sequence pools."""
        return {
            name: seq_pool_conf.get_sequence_pool(self)
            for (name, seq_pool_conf) in self.config.sequence_pools.items()
        }

    @Cachable.caching_property
    def trajectory_pool(self):
        """The instantiated TrajectoryPoolRunnerFactory"""
        return self.config.trajectory_pool.get_factory(self)

    @Cachable.caching_property
    def metrics(self):
        """The metrics work environment."""
        return MetricWorkEnv(self.config.metrics, self)

    @Cachable.caching_property
    def clusterers(self):
        """The dict of instantiated clusterers."""
        return {
            name: conf.get_clusterer(self)
            for (name, conf) in self.config.clusterers.items()
        }

    # @Cachable.caching_property
    # def visualizations(self):
    #     """The visualizations work environment."""
    #     return VisualizationWorkEnv(self.config.visualizations, self)

    @Cachable.caching_property
    def custom_components(self):
        """The dict of instantiated custom components."""
        custom_ops_dict = self.config.custom_operators
        return {
            name: conf.get_custom_operator() for name, conf in custom_ops_dict.items()
        }

    @Cachable.caching_property
    def functions(self):
        """
        The dict of instantiated functions.
        """
        return FunctionWorkEnv(self.config.functions, self)

    @Cachable.caching_property
    def loaders(self):
        """
        The dict of instantiated loaders.
        """
        return {name: conf.get_loader() for (name, conf) in self.config.loaders.items()}
