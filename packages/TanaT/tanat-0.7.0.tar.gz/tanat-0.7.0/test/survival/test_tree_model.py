#!/usr/bin/env python3
"""
Tests for Tree survival model.
"""

import pytest

from tanat.survival import SurvivalAnalysis
from tanat.survival.result import SurvivalResult
from tanat.survival.model.type.tree.settings import TreeSurvivalSettings


class TestTreeSurvival:
    """Tests for Tree survival analysis."""

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
    def test_tree_survival_array_generation(
        self, survival_train_pools, pool_type, query, tree_model, snapshot
    ):
        """Test survival array generation with parametrized pool types and queries."""
        sequence_pool = survival_train_pools[pool_type]

        # Generate survival array
        result = tree_model.get_survival_array(sequence_pool=sequence_pool, query=query)

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
    def test_tree_model_fitting_and_structure(
        self, survival_train_pools, pool_type, query, tree_model, snapshot
    ):
        """Test Tree model fitting and survival array structure verification."""
        sequence_pool = survival_train_pools[pool_type]

        # Generate survival array first to check structure
        result = tree_model.get_survival_array(sequence_pool=sequence_pool, query=query)

        # Fit the model
        tree_model.fit(sequence_pool=sequence_pool, query=query)

        # Verify model is fitted
        assert tree_model._model.is_fitted

        # Verify survival array structure
        assert result.survival_array.dtype.names == ("observed", "duration")

        # Snapshot test on survival array directly
        snapshot.assert_match(result.survival_array)

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'CONSULTATION'"),
            ("state", "condition == 'DIGESTIVE'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_tree_model_prediction_workflow(
        self,
        survival_train_pools,
        survival_predict_pools,
        pool_type,
        query,
        tree_model,
        snapshot,
    ):
        """Test complete Tree workflow: fit on train, predict on different set."""
        # Use parametrized pool and query for training
        train_pool = survival_train_pools[pool_type]
        predict_pool = survival_predict_pools[pool_type]

        # Generate survival array for training
        _ = tree_model.get_survival_array(sequence_pool=train_pool, query=query)

        # Fit on training data
        tree_model.fit(sequence_pool=train_pool, query=query)

        assert tree_model._model.is_fitted

        survival_functions = tree_model.predict_survival_function(predict_pool)

        # Snapshot test on survival functions directly
        snapshot.assert_match(survival_functions)

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'CONSULTATION'"),
            # no way to find a valid workaround
            # ("state", "condition == 'DIGESTIVE'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_tree_model_custom_settings(
        self, survival_train_pools, pool_type, query, snapshot
    ):
        """Test Tree model with custom settings."""
        # Create Tree model with custom settings
        custom_settings = TreeSurvivalSettings(
            max_depth=5,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            random_state=123,
        )

        tree_custom = SurvivalAnalysis("tree", settings=custom_settings)

        # Test with parametrized pool
        sequence_pool = survival_train_pools[pool_type]
        result = tree_custom.get_survival_array(
            sequence_pool=sequence_pool, query=query
        )

        assert isinstance(result, SurvivalResult)

        # Test fitting if we have data
        tree_custom.fit(sequence_pool=sequence_pool, query=query)

        assert tree_custom._model.is_fitted

        # Snapshot test on result and fitted status
        snapshot.assert_match(result)
