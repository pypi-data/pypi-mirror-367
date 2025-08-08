#!/usr/bin/env python3
"""Sequence pool simulation."""

## -- Shared
from tseqmock.generator.base.profile import Profile
from tseqmock.method.base import GenMethod
from tseqmock.time_strategy.base import TimeStrategy
from tseqmock.distribution.base import Distribution

## -- Event
from tseqmock.generator.type.event.time_design import EventTimeDesign

## -- State
from tseqmock.generator.type.state.time_design import StateTimeDesign

## -- Interval
from tseqmock.generator.type.interval.time_design import IntervalTimeDesign

## -- Sequence pool
from .mocker import SequencePoolMocker

## -- Utils
from .preset import (
    generate_event_sequences,
    generate_state_sequences,
    generate_interval_sequences,
)

__all__ = [
    ## -- Shared
    "Profile",
    "GenMethod",
    "TimeStrategy",
    "Distribution",
    ## -- Event
    "EventTimeDesign",
    ## -- State
    "StateTimeDesign",
    ## -- Interval
    "IntervalTimeDesign",
    ## -- Sequence pool
    "SequencePoolMocker",
    ## -- Utils
    "generate_event_sequences",
    "generate_state_sequences",
    "generate_interval_sequences",
]
