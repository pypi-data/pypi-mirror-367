#!/usr/bin/env python3
"""
Test query criterion applied to sequence pools.
"""

import pytest

from tanat.criterion.mixin.query.settings import QueryCriterion


class TestQueryCriterion:
    """
    Test query criterion applied to sequence pools.
    """

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_entity_level(self, sequence_pools, pool_type, query, snapshot):
        """
        Event/Interval Sequence pool: Query criterion applied to entity level (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()

        filtered_pool = pool.filter(
            QueryCriterion(query=query), level="entity", inplace=False
        )
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool.static_data.equals(pool.static_data)
        assert filtered_pool is not pool
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_entity_level_inplace(
        self, sequence_pools, pool_type, query, snapshot
    ):
        """
        Event/Interval Sequence pool: Query criterion applied to entity level (inplace=True).
        """
        pool = sequence_pools[pool_type]
        pool_copy = pool.copy()
        result = pool_copy.filter(
            QueryCriterion(query=query), level="entity", inplace=True
        )
        assert result is None
        assert pool_copy.static_data.equals(pool.static_data)
        snapshot.assert_match(pool_copy.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_entity_level_consistency(self, sequence_pools, pool_type, query):
        """
        Check filter entity level with inplace=True and inplace=False produce the same results.
        """
        original_pool = sequence_pools[pool_type]

        # -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            QueryCriterion(query=query), level="entity", inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(QueryCriterion(query=query), level="entity", inplace=True)
        inplace_result = pool_copy.sequence_data

        # -- test
        assert non_inplace_result.equals(inplace_result)
        assert filtered_pool_non_inplace.static_data.equals(original_pool.static_data)
        assert pool_copy.static_data.equals(original_pool.static_data)

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("state", "health_state == 'TREATMENT'"),
        ],
    )
    def test_filter_state_entity_level_error(self, sequence_pools, pool_type, query):
        """
        State Sequence pool: Query criterion applied to entity level raises error.
        """
        pool = sequence_pools[pool_type]

        with pytest.raises(NotImplementedError):
            pool.filter(QueryCriterion(query=query), level="entity", inplace=False)

        with pytest.raises(NotImplementedError):
            pool.filter(QueryCriterion(query=query), level="entity", inplace=True)

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_sequence_level(self, sequence_pools, pool_type, query, snapshot):
        """
        Sequence pool: Query criterion applied to sequence level (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()

        filtered_pool = pool.filter(
            QueryCriterion(query=query), level="sequence", inplace=False
        )
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool is not pool

        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_filter_sequence_level_inplace(
        self, sequence_pools, pool_type, query, snapshot
    ):
        """
        Sequence pool: Query criterion applied to sequence level (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        result = pool.filter(
            QueryCriterion(query=query), level="sequence", inplace=True
        )
        assert result is None
        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("interval", "administration_route"),
        ],
    )
    def test_filter_missing_values(self, sequence_pools, pool_type, col_name, snapshot):
        """
        Event/Interval Sequence pool: Query criterion applied to missing values (inplace=False).
        """
        pool = sequence_pools[pool_type]
        criterion = QueryCriterion(query=f"{col_name}.isna()")

        filtered_pool = pool.filter(criterion, level="entity", inplace=False)
        assert filtered_pool is not pool
        assert filtered_pool.static_data.equals(pool.static_data)
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("interval", "administration_route"),
        ],
    )
    def test_filter_missing_values_inplace(
        self, sequence_pools, pool_type, col_name, snapshot
    ):
        """
        Event/Interval Sequence pool: Query criterion applied to missing values (inplace=True).
        """
        pool = sequence_pools[pool_type]
        pool_copy = pool.copy()
        criterion = QueryCriterion(query=f"{col_name}.isna()")
        result = pool_copy.filter(criterion, level="entity", inplace=True)
        assert result is None
        assert pool_copy.static_data.equals(pool.static_data)
        snapshot.assert_match(pool_copy.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("interval", "administration_route"),
        ],
    )
    def test_filter_missing_values_consistency(
        self, sequence_pools, pool_type, col_name
    ):
        """
        Check filter missing values with inplace=True and inplace=False produce the same results.
        """
        original_pool = sequence_pools[pool_type]
        criterion = QueryCriterion(query=f"{col_name}.isna()")

        ## -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            criterion, level="entity", inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        ## -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(criterion, level="entity", inplace=True)
        inplace_result = pool_copy.sequence_data

        ## -- test
        assert non_inplace_result.equals(inplace_result)
        assert pool_copy.static_data.equals(original_pool.static_data)
        assert filtered_pool_non_inplace.static_data.equals(original_pool.static_data)

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("state", "condition"),
            ("interval", "administration_route"),
        ],
    )
    def test_filter_sequence_with_missing_values(
        self, sequence_pools, pool_type, col_name, snapshot
    ):
        """
        Sequence pool: Query criterion applied to missing values (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()
        criterion = QueryCriterion(query=f"{col_name}.isna()")

        filtered_pool = pool.filter(criterion, level="sequence", inplace=False)
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool is not pool

        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("state", "condition"),
            ("interval", "administration_route"),
        ],
    )
    def test_filter_sequence_with_missing_values_inplace(
        self, sequence_pools, pool_type, col_name, snapshot
    ):
        """
        Sequence pool: Query criterion applied to missing values (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        original_data = pool.sequence_data.copy()
        criterion = QueryCriterion(query=f"{col_name}.isna()")

        result = pool.filter(criterion, level="sequence", inplace=True)
        assert result is None
        assert not original_data.equals(pool.sequence_data)

        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("interval", "administration_route"),
        ],
    )
    def test_filter_no_matching_query_criterion_entity_level(
        self, sequence_pools, pool_type, col_name
    ):
        """
        Test filtering with query criterion at entity level that doesn't match any data.
        Should return an empty dataframe.
        """
        pool = sequence_pools[pool_type]

        query_criterion = QueryCriterion(query=f"{col_name} == 'FAKE ELT'")

        # Apply filter
        filtered_pool = pool.filter(query_criterion, level="entity", inplace=False)
        assert filtered_pool.sequence_data.empty
        assert filtered_pool.static_data.equals(pool.static_data)

        # Test with inplace=True
        pool_copy = pool.copy()
        result = pool_copy.filter(query_criterion, level="entity", inplace=True)
        assert result is None
        assert pool_copy.sequence_data.empty
        assert pool_copy.static_data.equals(pool.static_data)

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("state", "condition"),
            ("interval", "administration_route"),
        ],
    )
    def test_filter_no_matching_query_criterion_sequence_level(
        self, sequence_pools, pool_type, col_name
    ):
        """
        Test filtering with query criterion at sequence level that doesn't match any data.
        Should return an empty dataframe.
        """
        pool = sequence_pools[pool_type]

        query_criterion = QueryCriterion(query=f"{col_name} == 'FAKE ELT'")

        # Apply filter
        filtered_pool = pool.filter(query_criterion, level="sequence", inplace=False)
        assert filtered_pool.sequence_data.empty
        assert filtered_pool.static_data.empty

        # Test with inplace=True
        pool_copy = pool.copy()
        result = pool_copy.filter(query_criterion, level="sequence", inplace=True)
        assert result is None
        assert pool_copy.sequence_data.empty
        assert pool_copy.static_data.empty

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_which_query_criterion(self, sequence_pools, pool_type, query, snapshot):
        """Test which method for query criterion"""
        pool = sequence_pools[pool_type]
        query_criterion = QueryCriterion(query=query)
        matching_ids = pool.which(query_criterion)
        assert isinstance(matching_ids, set)
        snapshot.assert_match(sorted(matching_ids))

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_query_criterion_consistency(self, sequence_pools, pool_type, query):
        """
        Check filtering sequence consistency.
        """
        original_pool = sequence_pools[pool_type]

        # -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            QueryCriterion(query=query), level="sequence", inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(QueryCriterion(query=query), level="sequence", inplace=True)
        inplace_result = pool_copy.sequence_data

        ## -- which
        matching_ids = sorted(original_pool.which(QueryCriterion(query=query)))

        ## -- test
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids

    @pytest.mark.parametrize(
        "pool_type,col_name",
        [
            ("event", "provider"),
            ("state", "condition"),
            ("interval", "administration_route"),
        ],
    )
    def test_missing_value_query_criterion_consistency(
        self, sequence_pools, pool_type, col_name
    ):
        """
        Test filtering missing value consistency.
        """
        original_pool = sequence_pools[pool_type]
        criterion = QueryCriterion(query=f"{col_name}.isna()")

        ## -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            criterion, level="sequence", inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        ## -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(criterion, level="sequence", inplace=True)
        inplace_result = pool_copy.sequence_data

        ## -- which
        matching_ids = sorted(original_pool.which(criterion))

        ## -- tests
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids

    @pytest.mark.parametrize(
        "pool_type,query",
        [
            ("event", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'TREATMENT'"),
            ("interval", "medication == 'ANTIBIOTIC'"),
        ],
    )
    def test_query_sequence_filtering_via_dict_criterion(
        self, sequence_pools, pool_type, query
    ):
        """
        Verify consistency of sequence filtering using criterion defined in a dictionary.
        """
        original_pool = sequence_pools[pool_type]

        query_criterion_dict = {"query": query}

        # -- non inplace filtering
        filtered_pool_non_inplace = original_pool.filter(
            criterion=query_criterion_dict,
            criterion_type="query",
            level="sequence",
            inplace=False,
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # -- inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(
            criterion=query_criterion_dict,
            criterion_type="query",
            level="sequence",
            inplace=True,
        )
        inplace_result = pool_copy.sequence_data

        # -- determine matching IDs
        matching_ids = sorted(
            original_pool.which(
                criterion=query_criterion_dict,
                criterion_type="query",
            )
        )

        # -- assertions
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids
