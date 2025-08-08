#!/usr/bin/env python3
"""
Global fixtures.
"""

import os

import pytest

import pandas as pd

from tanat.sequence.base.pool import SequencePool
from tanat.trajectory.pool import TrajectoryPool


def load_csv(filename, **kwargs):
    """Helper function to load CSV files"""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    return pd.read_csv(os.path.join(data_dir, filename), **kwargs)


@pytest.fixture(scope="session")
def pool_data():
    """Load pre-generated pool data from CSV files"""
    event_data = load_csv("event/complex_data.csv", parse_dates=["date"])
    state_data = load_csv(
        "state/complex_data.csv", parse_dates=["start_date", "end_date"]
    )
    interval_data = load_csv(
        "interval/complex_data.csv", parse_dates=["start_date", "end_date"]
    )
    static_data = load_csv("static/static_data.csv")

    return {
        "event": event_data,
        "state": state_data,
        "interval": interval_data,
        "static_data": static_data,
    }


@pytest.fixture(scope="session")
def sequence_pools(pool_data):
    """Create sequence pools from pool data"""
    # Event sequence pool settings
    event_settings = {
        "id_column": "patient_id",
        "time_column": "date",
        "entity_features": ["event_type", "provider"],
        "static_features": ["gender", "age", "insurance", "chronic_condition"],
    }

    # State sequence pool settings
    state_settings = {
        "id_column": "patient_id",
        "entity_features": ["health_state", "condition"],
        "start_column": "start_date",
        "end_column": "end_date",
        "static_features": ["gender", "age", "insurance", "chronic_condition"],
    }

    # Interval sequence pool settings
    interval_settings = {
        "id_column": "patient_id",
        "entity_features": ["medication", "administration_route", "dosage"],
        "start_column": "start_date",
        "end_column": "end_date",
        "static_features": ["gender", "age", "insurance", "chronic_condition"],
    }

    # Create sequence pools
    seqpool_event = SequencePool.init(
        "event",
        pool_data["event"],
        event_settings,
        metadata=None,
        static_data=pool_data["static_data"],
    )

    seqpool_state = SequencePool.init(
        "state",
        pool_data["state"],
        state_settings,
        metadata=None,
        static_data=pool_data["static_data"],
    )

    seqpool_interval = SequencePool.init(
        "interval",
        pool_data["interval"],
        interval_settings,
        metadata=None,
        static_data=pool_data["static_data"],
    )

    return {
        "event": seqpool_event,
        "state": seqpool_state,
        "interval": seqpool_interval,
    }


@pytest.fixture(scope="session")
def trajectory_pool(sequence_pools):
    """Create trajectory pool from sequence pools"""
    # Create a trajectory pool
    traj_pool = TrajectoryPool.init_empty()

    # Add sequence pools to trajectory pool
    traj_pool.add_sequence_pool(sequence_pools["event"], "event")
    traj_pool.add_sequence_pool(sequence_pools["state"], "state")
    traj_pool.add_sequence_pool(sequence_pools["interval"], "interval")

    # Add static data
    static_data = sequence_pools["event"].static_data
    traj_pool.add_static_features(
        static_data,
        id_column="patient_id",
        static_features=["gender", "age", "insurance", "chronic_condition"],
    )

    return traj_pool


@pytest.fixture(scope="session")
def single_id_data(pool_data):
    """Create a single sequence data (unique ID)"""
    # Get patient ID
    patient_id = pool_data["static_data"]["patient_id"].iloc[0]

    ## -- Filter by patient ID
    def filter_by_id(df):
        return df[df["patient_id"] == patient_id]

    event_data = filter_by_id(pool_data["event"])
    state_data = filter_by_id(pool_data["state"])
    interval_data = filter_by_id(pool_data["interval"])
    static_data = filter_by_id(pool_data["static_data"])

    return {
        "event": event_data,
        "state": state_data,
        "interval": interval_data,
        "static_data": static_data,
    }
