#!/usr/bin/env python3
"""
Function working environment.
"""

from pypassist.runner.workenv.base.workenv import BaseWorkEnv
from pypassist.mixin.cachable import Cachable


class FunctionWorkEnv(BaseWorkEnv, Cachable):
    """Function work environment."""

    def __init__(self, config, parent_env=None):
        BaseWorkEnv.__init__(self, config, parent_env)
        Cachable.__init__(self)

    @Cachable.caching_property
    def aggregation(self):
        """
        The dict of instantiated aggregation functions.
        """
        return self._get_functions("aggregation")

    def _get_functions(self, section_name):
        """
        Common internal method for retrieving dicts of instances of functions.

        Args:
            section_name:
                The name of the section of the configuration file (e.g.
                "aggregation").
        """
        section = getattr(self.config, section_name)
        return {
            name: conf.get_function(self.parent_env) for (name, conf) in section.items()
        }
