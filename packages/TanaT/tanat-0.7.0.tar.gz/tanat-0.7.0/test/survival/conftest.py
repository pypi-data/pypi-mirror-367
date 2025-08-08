#!/usr/bin/env python3
"""
Survival test fixtures using base test data.
"""

import pytest
from tanat.sequence.base.pool import SequencePool
from tanat.survival import SurvivalAnalysis


@pytest.fixture(scope="session")
def survival_train_pools(pool_data):
    """Create training sequence pools from base test data sliced by ID."""
    # Get first 3 patient IDs for training
    unique_ids = pool_data["static_data"]["patient_id"].unique()
    train_ids = unique_ids[:7]  # 70% of data for training

    # Filter data for training
    train_event = pool_data["event"][
        pool_data["event"]["patient_id"].isin(train_ids)
    ].copy()
    train_state = pool_data["state"][
        pool_data["state"]["patient_id"].isin(train_ids)
    ].copy()
    train_interval = pool_data["interval"][
        pool_data["interval"]["patient_id"].isin(train_ids)
    ].copy()
    train_static = pool_data["static_data"][
        pool_data["static_data"]["patient_id"].isin(train_ids)
    ].copy()

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

    # Create training sequence pools
    train_event_pool = SequencePool.init(
        "event",
        train_event,
        event_settings,
        metadata=None,
        static_data=train_static,
    )

    train_state_pool = SequencePool.init(
        "state",
        train_state,
        state_settings,
        metadata=None,
        static_data=train_static,
    )

    train_interval_pool = SequencePool.init(
        "interval",
        train_interval,
        interval_settings,
        metadata=None,
        static_data=train_static,
    )

    # Set t_zero for survival analysis
    train_event_pool.t_zero = "2023-01-01"
    train_state_pool.t_zero = "2023-01-01"
    train_interval_pool.t_zero = "2023-01-01"

    return {
        "event": train_event_pool,
        "state": train_state_pool,
        "interval": train_interval_pool,
    }


@pytest.fixture(scope="session")
def survival_predict_pools(pool_data):
    """Create prediction sequence pools from base test data sliced by ID."""
    # Get remaining patient IDs for prediction
    unique_ids = pool_data["static_data"]["patient_id"].unique()
    predict_ids = unique_ids[7:]  # 30% of data for prediction

    # Filter data for prediction
    predict_event = pool_data["event"][
        pool_data["event"]["patient_id"].isin(predict_ids)
    ].copy()
    predict_state = pool_data["state"][
        pool_data["state"]["patient_id"].isin(predict_ids)
    ].copy()
    predict_interval = pool_data["interval"][
        pool_data["interval"]["patient_id"].isin(predict_ids)
    ].copy()
    predict_static = pool_data["static_data"][
        pool_data["static_data"]["patient_id"].isin(predict_ids)
    ].copy()

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

    # Create prediction sequence pools
    predict_event_pool = SequencePool.init(
        "event",
        predict_event,
        event_settings,
        metadata=None,
        static_data=predict_static,
    )

    predict_state_pool = SequencePool.init(
        "state",
        predict_state,
        state_settings,
        metadata=None,
        static_data=predict_static,
    )

    predict_interval_pool = SequencePool.init(
        "interval",
        predict_interval,
        interval_settings,
        metadata=None,
        static_data=predict_static,
    )

    # Set t_zero for survival analysis
    predict_event_pool.t_zero = "2023-01-01"
    predict_state_pool.t_zero = "2023-01-01"
    predict_interval_pool.t_zero = "2023-01-01"

    return {
        "event": predict_event_pool,
        "state": predict_state_pool,
        "interval": predict_interval_pool,
    }


@pytest.fixture(
    scope="session",
    params=[
        ("event", "event_type == 'EXAM'"),
        ("event", "event_type == 'CONSULTATION'"),
        ("state", "health_state == 'CONVALESCENCE'"),
        ("state", "health_state == 'CHRONIC_MONITORING'"),
        ("interval", "medication == 'ANTIBIOTIC'"),
    ],
)
def pool_type_and_query(request):
    """Parametrized fixture for sequence pool types and associated queries."""
    return request.param


@pytest.fixture(scope="session")
def cox_model():
    """Create Cox survival model for testing."""
    # Avoid using age to prevent error in survival analysis
    settings = {
        "static_features": [
            "gender",
            "chronic_condition",
        ]
    }
    return SurvivalAnalysis("coxnet", settings=settings)


@pytest.fixture(scope="session")
def tree_model():
    """Create Tree survival model for testing."""
    # Avoid using age to prevent error in survival analysis
    settings = {
        "static_features": [
            "gender",
            "chronic_condition",
        ]
    }
    return SurvivalAnalysis("tree", settings=settings)


@pytest.fixture(
    scope="session",
    params=[
        ("event", "event_type == 'CONSULTATION'"),
        ("state", "health_state == 'HEALTHY'"),
        ("interval", "medication == 'ANTIBIOTIC'"),
    ],
)
def pool_type_and_specific_query(request):
    """Parametrized fixture for sequence pool types with specific queries for detailed testing."""
    return request.param
