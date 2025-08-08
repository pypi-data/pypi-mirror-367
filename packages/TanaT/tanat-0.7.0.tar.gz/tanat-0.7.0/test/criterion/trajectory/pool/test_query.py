#!/usr/bin/env python3
"""
Test query criterion applied to trajectory pools.
"""

import pytest

from tanat.criterion.mixin.query.settings import QueryCriterion
from tanat.criterion.base.exception import InvalidCriterionError


class TestQueryCriterion:
    """
    Test query criterion applied to trajectory pools.
    """

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_trajectories_on_sequence_level(
        self, trajectory_pool, sequence_name, query, snapshot
    ):
        """
        Trajectory pool: Query criterion applied to sequence level (inplace=False).
        """
        query_criterion = QueryCriterion(query=query)
        filtered_pool = trajectory_pool.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))
        assert filtered_pool.settings.intersection is True

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_trajectories_on_entity_level(
        self, trajectory_pool, sequence_name, query, snapshot
    ):
        """
        Test filtering trajectories on entity level.
        """
        query_criterion = QueryCriterion(query=query)
        filtered_pool = trajectory_pool.filter(
            criterion=query_criterion,
            level="entity",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )

        snapshot.assert_match(sorted(filtered_pool.unique_ids))
        assert filtered_pool.settings.intersection is True

    def test_filter_entity_level_raises_error_on_state(self, trajectory_pool):
        """
        Test filtering entity level raises error on state.
        """
        criterion = QueryCriterion(query="health_state == 'TREATMENT'")
        with pytest.raises(NotImplementedError):
            trajectory_pool.filter(
                criterion=criterion,
                level="entity",
                sequence_name="state",
                inplace=False,
                intersection=True,
            )

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_trajectories_on_sequence_level_inplace(
        self, trajectory_pool, sequence_name, query, snapshot
    ):
        """
        Trajectory pool: Query criterion applied to sequence level (inplace=True).
        """
        query_criterion = QueryCriterion(query=query)

        ## -- filtering on copy
        trajectory_pool_copy = trajectory_pool.copy()
        filtered_pool = trajectory_pool_copy.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        ## -- inplace should return None
        assert filtered_pool is None
        snapshot.assert_match(sorted(trajectory_pool_copy.unique_ids))

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_trajectories_on_sequence_level_consistency(
        self, trajectory_pool, sequence_name, query
    ):
        """
        Check filter sequence level with inplace=True and inplace=False produce the same results.
        """
        ## -- query criterion
        query_criterion = QueryCriterion(query=query)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        non_inplace_result = sorted(filtered_pool.unique_ids)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type.isin(['EMERGENCY', 'SPECIALIST'])"),
            ("state", "health_state.isin(['TREATMENT', 'CONVALESCENCE'])"),
            ("interval", "medication.isin(['ANTIBIOTIC', 'PAIN_RELIEVER'])"),
        ],
    )
    def test_filter_trajectories_with_multiple_conditions(
        self, trajectory_pool, sequence_name, query, snapshot
    ):
        """
        Test filtering with multiple conditions in the query.
        """
        ## -- query criterion with multiple conditions
        query_criterion = QueryCriterion(query=query)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'NONEXISTENT_EVENT'"),
            ("state", "health_state == 'NONEXISTENT_STATE'"),
            ("interval", "medication == 'NONEXISTENT_MEDICATION'"),
        ],
    )
    def test_filter_no_matching_query_criterion(
        self, trajectory_pool, sequence_name, query
    ):
        """
        Test filtering with query criterion that doesn't match any data.
        Should return an empty trajectory pool.
        """
        ## -- query criterion with non-existent value
        query_criterion = QueryCriterion(query=query)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )

        assert filtered_pool.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'NONEXISTENT_EVENT'"),
            ("state", "health_state == 'NONEXISTENT_STATE'"),
            ("interval", "medication == 'NONEXISTENT_MEDICATION'"),
        ],
    )
    def test_filter_no_matching_query_criterion_inplace(
        self, trajectory_pool, sequence_name, query
    ):
        """
        Test filtering with query criterion that doesn't match any data (inplace=True).
        Should result in an empty trajectory pool.
        """
        ## -- query criterion with non-existent value
        query_criterion = QueryCriterion(query=query)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        # Test empty result
        assert traj_pool_copy.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_query_filtering_via_dict_criterion(
        self, trajectory_pool, sequence_name, query
    ):
        """
        Verify consistency of filtering using criterion defined in a dictionary.
        """
        # Dictionary criterion
        dict_criterion = {"query": query}

        # Non-inplace filtering with dict criterion
        filtered_pool = trajectory_pool.filter(
            criterion=dict_criterion,
            criterion_type="query",
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        non_inplace_result = sorted(filtered_pool.unique_ids)

        # Inplace filtering with dict criterion
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=dict_criterion,
            criterion_type="query",
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "sequence_name,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_intersection_false(self, trajectory_pool, sequence_name, query, snapshot):
        """
        Test that setting intersection=False does not affect the length of the filtered
        trajectory pool, but does affect the length of the inner sequence pool.
        """
        query_criterion = QueryCriterion(query=query)
        filtered_pool = trajectory_pool.filter(
            criterion=query_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=False,
        )

        assert len(filtered_pool) == len(trajectory_pool)
        assert filtered_pool.settings.intersection is False
        filtered_sequence_ids = sorted(
            filtered_pool.sequence_pools[sequence_name].unique_ids
        )
        snapshot.assert_match(filtered_sequence_ids)

    def test_which_method_raises_error(self, trajectory_pool):
        """
        Which method should raise an error for query criterion because this criterion is not
        applicable at 'trajectory' level.
        """

        criterion_kwargs = {"query": 'FAKE_COLUMN == "dummy_value"'}
        criterion = QueryCriterion(**criterion_kwargs)

        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion_kwargs, criterion_type="query")
