#!/usr/bin/env python3
"""Criterion package."""

## -- sequence + entity level
from .mixin.query.settings import QueryCriterion
from .mixin.pattern.settings import PatternCriterion
from .mixin.time.settings import TimeCriterion

## -- sequence level only
from .sequence.type.length.settings import LengthCriterion

## -- trajectory + sequence level
from .mixin.static.settings import StaticCriterion

__all__ = [
    "QueryCriterion",
    "PatternCriterion",
    "TimeCriterion",
    "LengthCriterion",
    "StaticCriterion",
]
