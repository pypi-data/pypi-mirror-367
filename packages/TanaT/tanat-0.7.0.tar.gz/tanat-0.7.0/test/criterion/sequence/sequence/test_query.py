#!/usr/bin/env python3
"""
Test query criterion applied to a single sequence.
"""

import pytest

from tanat.criterion.mixin.query.settings import QueryCriterion


class TestQueryCriterion:
    """
    Test the query match method applied to individual sequence.
    """

    @pytest.mark.parametrize(
        "pool_type,query,sequence_id,expected_result",
        [
            ("event", "event_type == 'EMERGENCY'", 1, True),
            ("event", "event_type == 'FAKE_EVENT'", 4, False),
            ("state", "health_state == 'HEALTHY'", 1, True),
            ("state", "health_state == 'FAKE_STATE'", 2, False),
            ("interval", "medication == 'ANTIBIOTIC'", 4, True),
            ("interval", "medication == 'FAKE_MEDICATION'", 2, False),
        ],
    )
    def test_match_with_query_criterion(
        self, sequence_pools, pool_type, query, sequence_id, expected_result
    ):
        """
        Test if a specific sequence matches query criterion.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        # Test with QueryCriterion object
        criterion = QueryCriterion(query=query)
        result = sequence.match(criterion)
        assert result == expected_result

        # Test with dictionary
        criterion_dict = {"query": query}
        result = sequence.match(criterion_dict, criterion_type="query")
        assert result == expected_result

    @pytest.mark.parametrize(
        "pool_type,col_name,sequence_id,expected_result",
        [
            ("event", "provider", 1, True),
            ("event", "provider", 4, False),
            ("state", "condition", 1, True),
            ("state", "condition", 3, False),
            ("interval", "administration_route", 1, True),
            ("interval", "administration_route", 3, False),
        ],
    )
    def test_match_with_missing_values(
        self, sequence_pools, pool_type, col_name, sequence_id, expected_result
    ):
        """
        Test if a specific sequence contains missing values according to criterion.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        # Test with QueryCriterion object
        criterion = QueryCriterion(query=f"{col_name}.isna()")
        result = sequence.match(criterion)
        assert result == expected_result

        # Test with dictionary
        criterion_dict = {"query": f"{col_name}.isna()"}
        result = sequence.match(criterion_dict, criterion_type="query")
        assert result == expected_result

    @pytest.mark.parametrize(
        "pool_type,base_query,override_query",
        [
            ("event", "event_type == 'FAKE_EVENT'", "event_type == 'EMERGENCY'"),
            ("state", "health_state == 'FAKE_STATE'", "health_state == 'REMISSION'"),
            (
                "interval",
                "medication == 'FAKE_MEDICATION'",
                "medication == 'ANTIBIOTIC'",
            ),
        ],
    )
    def test_match_with_criterion_kwargs_override(
        self, sequence_pools, pool_type, base_query, override_query
    ):
        """
        Test if kwargs can override criterion parameters.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[4]

        # Create base criterion
        base_criterion = QueryCriterion(query=base_query)

        # Check that sequence doesn't match base criterion
        assert not sequence.match(base_criterion)

        # Override the query with a parameter that should match
        result = sequence.match(base_criterion, query=override_query)
        assert result

        # Do the same with a dictionary
        base_dict = {"query": base_query}
        result = sequence.match(base_dict, criterion_type="query", query=override_query)
        assert result

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            ("event", 1, {"query": "event_type == 'EMERGENCY'"}),
            ("interval", 4, {"query": "medication == 'ANTIBIOTIC'"}),
        ],
    )
    def test_filter_entities_inplace(
        self, sequence_pools, pool_type, sequence_id, criterion_kwargs, snapshot
    ):
        """
        Filter at entity level.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]
        criterion = QueryCriterion(**criterion_kwargs)
        result = sequence.filter(criterion, inplace=True)

        assert result is None
        snapshot.assert_match(sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            ("event", 1, {"query": "event_type == 'EMERGENCY'"}),
            ("interval", 4, {"query": "medication == 'ANTIBIOTIC'"}),
        ],
    )
    def test_filter_entities_non_inplace(
        self, sequence_pools, pool_type, sequence_id, criterion_kwargs, snapshot
    ):
        """
        Filter at entity level with non-inplace.
        """
        pool = sequence_pools[pool_type]
        sequence_copy = pool[sequence_id].copy()
        criterion = QueryCriterion(**criterion_kwargs)
        sequence = sequence_copy.filter(criterion, inplace=False)
        snapshot.assert_match(sequence.sequence_data.to_csv())

    def test_filter_entities_on_state_sequence_raises_not_implemented_error(
        self, sequence_pools
    ):
        """
        Filter entities should raise a NotImplementedError.
        """
        state_pool = sequence_pools["state"]
        sequence = state_pool[1]
        criterion_kwargs = {"query": "FAKE_COL == 'dummy_value'"}
        criterion = QueryCriterion(**criterion_kwargs)

        with pytest.raises(NotImplementedError):
            sequence.filter(criterion)

        ## -- from dict
        with pytest.raises(NotImplementedError):
            sequence.filter(criterion_kwargs, criterion_type="query")
