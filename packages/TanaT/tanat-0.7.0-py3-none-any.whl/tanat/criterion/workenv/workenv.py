#!/usr/bin/env python3
"""
Criterion working environment.
"""

from pypassist.runner.workenv.base.workenv import BaseWorkEnv
from pypassist.mixin.cachable import Cachable


class CriterionWorkEnv(BaseWorkEnv, Cachable):
    """Criterion work environment."""

    def __init__(self, config, parent_env=None):
        BaseWorkEnv.__init__(self, config, parent_env)
        Cachable.__init__(self)

    @Cachable.caching_property
    def static(self):
        """The dict of instantiated static criterion."""
        return {
            name: conf.get_criterion() for (name, conf) in self.config.static.items()
        }

    @Cachable.caching_property
    def sequence(self):
        """The dict of instantiated sequence criterion."""
        return {
            name: conf.get_criterion() for (name, conf) in self.config.sequence.items()
        }

    @Cachable.caching_property
    def trajectory(self):
        """The dict of instantiated trajectory criterion."""
        return {
            name: conf.get_criterion(self)
            for (name, conf) in self.config.trajectory.items()
        }
