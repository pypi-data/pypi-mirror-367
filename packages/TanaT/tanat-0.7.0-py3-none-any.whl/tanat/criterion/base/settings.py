#!/usr/bin/env python3
"""
Base class for criterion.
"""

import dataclasses

from .enum import CriterionLevel


@dataclasses.dataclass
class Criterion:
    """
    Base class for criterion.
    """

    _REGISTER_NAME = None

    def get_compatibility_levels(self, max_level=CriterionLevel.TRAJECTORY):
        """List the compatibility levels of the criterion.
        Compatibility levels are marked with decorators.

        Args:
            max_level (CriterionLevel, optional): The maximum level to consider.
                Defaults to Trajectory. Entity < Sequence < Trajectory

        Returns a list of CriterionLevel representing the compatibility levels of the
        criterion. The levels are "sequence","entity" or "trajectory".
        """
        if isinstance(max_level, str):
            max_level = CriterionLevel.from_str(max_level)

        compatibility_levels = getattr(self, "COMPATIBILITY_LEVELS", set())
        return [level for level in compatibility_levels if level <= max_level]
