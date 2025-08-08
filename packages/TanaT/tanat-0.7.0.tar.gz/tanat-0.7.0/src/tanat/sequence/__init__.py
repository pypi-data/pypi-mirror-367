#!/usr/bin/env python3
"""Sequence package."""

## -- Event sequence
from .type.event.pool import EventSequencePool
from .type.event.sequence import EventSequence
from .type.event.settings import EventSequenceSettings

## -- State sequence
from .type.state.pool import StateSequencePool
from .type.state.sequence import StateSequence
from .type.state.settings import StateSequenceSettings

## -- Interval sequence
from .type.interval.pool import IntervalSequencePool
from .type.interval.sequence import IntervalSequence
from .type.interval.settings import IntervalSequenceSettings

## -- Metadata
from .metadata.metadata import Metadata

__all__ = [
    "EventSequencePool",
    "EventSequence",
    "EventSequenceSettings",
    "StateSequencePool",
    "StateSequence",
    "StateSequenceSettings",
    "IntervalSequencePool",
    "IntervalSequence",
    "IntervalSequenceSettings",
    "Metadata",
]
