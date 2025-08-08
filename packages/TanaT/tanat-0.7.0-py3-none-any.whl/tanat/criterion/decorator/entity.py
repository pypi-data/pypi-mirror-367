#!/usr/bin/env python3
"""
Decorator for marking a criterion class as compatible with entity-level operations.
"""

from ..base.enum import CriterionLevel


def entity_compatible(cls):
    """Mark a criterion class as compatible with entity-level operations."""
    cls.COMPATIBILITY_LEVELS = getattr(cls, "COMPATIBILITY_LEVELS", set())
    cls.COMPATIBILITY_LEVELS.add(CriterionLevel.ENTITY)
    return cls
