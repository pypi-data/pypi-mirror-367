#!/usr/bin/env python3
"""
Decorator for marking a criterion class as compatible with sequence-level operations.
"""

from ..base.enum import CriterionLevel


def sequence_compatible(cls):
    """Mark a criterion class as compatible with sequence-level operations."""
    cls.COMPATIBILITY_LEVELS = getattr(cls, "COMPATIBILITY_LEVELS", set())
    cls.COMPATIBILITY_LEVELS.add(CriterionLevel.SEQUENCE)
    return cls
