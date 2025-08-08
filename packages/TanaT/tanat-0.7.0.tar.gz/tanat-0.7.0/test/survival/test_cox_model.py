#!/usr/bin/env python3
"""
Tests for Cox survival model.
"""

import pytest

from tanat.survival import SurvivalAnalysis
from tanat.survival.result import SurvivalResult
from tanat.survival.model.type.cox.settings import CoxnetSurvivalSettings


class TestCoxSurvival:
    """Tests for Cox survival analysis."""

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EXAM'"),
            ("event", "event_type == 'CONSULTATION'"),
            ("state", "health_state == 'CONVALESCENCE'"),
            ("state", "health_state == 'CHRONIC_MONITORING'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_cox_survival_array_generation(
        self, survival_train_pools, pool_type, query, cox_model, snapshot
    ):
        """Test survival array generation with parametrized pool types and queries."""
        sequence_pool = survival_train_pools[pool_type]

        # Generate survival array
        result = cox_model.get_survival_array(sequence_pool=sequence_pool, query=query)

        # Verify result structure
        assert isinstance(result, SurvivalResult)
        assert result.survival_array.dtype.names == ("observed", "duration")
        # Snapshot test on actual result
        snapshot.assert_match(result)

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EXAM'"),
            ("event", "event_type == 'CONSULTATION'"),
            ("state", "health_state == 'CONVALESCENCE'"),
            ("state", "health_state == 'CHRONIC_MONITORING'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_cox_model_fitting_and_structure(
        self, survival_train_pools, pool_type, query, cox_model, snapshot
    ):
        """Test Cox model fitting and survival array structure verification."""
        sequence_pool = survival_train_pools[pool_type]

        # Generate survival array first to check structure
        result = cox_model.get_survival_array(sequence_pool=sequence_pool, query=query)

        # Fit the model
        cox_model.fit(sequence_pool=sequence_pool, query=query)

        # Verify model is fitted
        assert cox_model._model.is_fitted

        # Verify survival array structure
        assert result.survival_array.dtype.names == ("observed", "duration")
        # Snapshot test on survival array directly
        snapshot.assert_match(result.survival_array)

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'CONSULTATION'"),
            ("state", "health_state == 'HEALTHY'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_cox_model_prediction_workflow(
        self,
        survival_train_pools,
        survival_predict_pools,
        pool_type,
        query,
        cox_model,
        snapshot,
    ):
        """Test complete Cox workflow: fit on train, predict on different set."""
        # Use parametrized pool and query for training
        train_pool = survival_train_pools[pool_type]
        predict_pool = survival_predict_pools[pool_type]

        # Generate survival array for training
        _ = cox_model.get_survival_array(sequence_pool=train_pool, query=query)

        # Fit on training data
        cox_model.fit(sequence_pool=train_pool, query=query)

        assert cox_model._model.is_fitted

        # Predict on different set
        survival_functions = cox_model.predict_survival_function(predict_pool)

        # Snapshot test on survival functions directly
        snapshot.assert_match(survival_functions)

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'CONSULTATION'"),
            ("state", "health_state == 'HEALTHY'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_cox_model_custom_settings(
        self, survival_train_pools, pool_type, query, snapshot
    ):
        """Test Cox model with custom settings."""
        # Create Cox model with custom settings
        custom_settings = CoxnetSurvivalSettings(
            l1_ratio=0.8, n_alphas=50, normalize=True, max_iter=5000
        )

        cox_custom = SurvivalAnalysis("coxnet", settings=custom_settings)

        # Test with parametrized pool
        sequence_pool = survival_train_pools[pool_type]
        result = cox_custom.get_survival_array(sequence_pool=sequence_pool, query=query)

        assert isinstance(result, SurvivalResult)

        # Fit the model
        cox_custom.fit(sequence_pool=sequence_pool, query=query)

        assert cox_custom._model.is_fitted

        # Snapshot test on result and fitted status
        snapshot.assert_match(result)
