#!/usr/bin/env python3
"""
Test pattern criterion applied to sequence pools.
"""

import pytest

from tanat.criterion.mixin.pattern.settings import PatternCriterion
from tanat.criterion.mixin.pattern.exception import InvalidColumnPatternError


class TestPatternCriterion:
    """
    Test pattern criterion applied to sequence pools.
    """

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_entity_level(self, sequence_pools, pool_type, pattern, snapshot):
        """
        Event/Interval Sequence pool: Pattern criterion applied to entity level (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()

        filtered_pool = pool.filter(
            PatternCriterion(pattern=pattern), level="entity", inplace=False
        )
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool is not pool
        assert filtered_pool.static_data.equals(
            pool.static_data
        )  # static data should be the same
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_entity_level_inplace(
        self, sequence_pools, pool_type, pattern, snapshot
    ):
        """
        Event/Interval Sequence pool: Pattern criterion applied to entity level (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        result = pool.filter(
            PatternCriterion(pattern=pattern), level="entity", inplace=True
        )
        assert result is None
        assert pool.static_data.equals(pool.static_data)
        snapshot.assert_match(pool.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_entity_level_consistency(self, sequence_pools, pool_type, pattern):
        """
        Check filter entity level with inplace=True and inplace=False produce the same results.
        """
        original_pool = sequence_pools[pool_type]

        ## -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            PatternCriterion(pattern=pattern), level="entity", inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        ## -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(
            PatternCriterion(pattern=pattern), level="entity", inplace=True
        )
        inplace_result = pool_copy.sequence_data

        ## -- test
        assert non_inplace_result.equals(inplace_result)

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("state", {"health_state": "TREATMENT"}),
        ],
    )
    def test_filter_state_entity_level_error(self, sequence_pools, pool_type, pattern):
        """
        State Sequence pool: Pattern criterion applied to entity level raises error.
        """
        pool = sequence_pools[pool_type]

        with pytest.raises(NotImplementedError):
            pool.filter(
                PatternCriterion(pattern=pattern), level="entity", inplace=False
            )

        with pytest.raises(NotImplementedError):
            pool.filter(PatternCriterion(pattern=pattern), level="entity", inplace=True)

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": ["EMERGENCY", "CONSULTATION"]}),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_filter_sequence_level(self, sequence_pools, pool_type, pattern, snapshot):
        """
        Sequence pool: Pattern criterion applied to sequence level (inplace=False).
        """
        pool = sequence_pools[pool_type]
        original_data = pool.sequence_data.copy()
        criterion = PatternCriterion(pattern=pattern, contains=True)

        filtered_pool = pool.filter(criterion, level="sequence", inplace=False)
        assert pool.sequence_data.equals(original_data)
        assert filtered_pool is not pool
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": ["EMERGENCY", "CONSULTATION"]}),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_filter_sequence_level_inplace(
        self, sequence_pools, pool_type, pattern, snapshot
    ):
        """
        Sequence pool: Pattern criterion applied to sequence level (inplace=True).
        """
        pool = sequence_pools[pool_type].copy()
        criterion = PatternCriterion(pattern=pattern, contains=True)
        result = pool.filter(criterion, level="sequence", inplace=True)
        assert result is None
        snapshot.assert_match(pool.sequence_data.to_csv())
        snapshot.assert_match(pool.static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,level,pattern",
        [
            ("event", "entity", {"FAKE_COL": ["EMERGENCY", "CONSULTATION"]}),
            ("interval", "entity", {"FAKE_COL": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
            ("event", "sequence", {"FAKE_COL": ["EMERGENCY", "CONSULTATION"]}),
            ("state", "sequence", {"FAKE_COL": ["TREATMENT", "CONVALESCENCE"]}),
            ("interval", "sequence", {"FAKE_COL": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_filter_raises_on_invalid_column(
        self, sequence_pools, pool_type, level, pattern
    ):
        """
        Ensure that filtering a sequence pool with an invalid column name
        in the pattern raises an InvalidColumnPatternError, both with
        inplace=False and inplace=True.
        """
        original_pool = sequence_pools[pool_type]
        criterion = PatternCriterion(pattern=pattern, contains=True)

        with pytest.raises(InvalidColumnPatternError):
            _ = original_pool.filter(criterion, level=level, inplace=False)

        with pytest.raises(InvalidColumnPatternError):
            pool_copy = original_pool.copy()
            pool_copy.filter(criterion, level=level, inplace=True)

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": "FAKE_PATTERN"}),
            ("interval", {"medication": "FAKE_PATTERN"}),
        ],
    )
    def test_filter_no_matching_pattern_criterion_entity_level(
        self, sequence_pools, pool_type, pattern
    ):
        """
        Test filtering with pattern criterion at entity level that doesn't match any data.
        Should return an empty dataframe.
        """
        original_pool = sequence_pools[pool_type]
        criterion = PatternCriterion(pattern=pattern, contains=True)

        # -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            criterion, level="entity", inplace=False
        )
        ## -- test
        assert filtered_pool_non_inplace.sequence_data.empty
        assert filtered_pool_non_inplace.static_data.equals(original_pool.static_data)

        # -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(criterion, level="entity", inplace=True)

        ## -- test
        assert pool_copy.sequence_data.empty
        assert pool_copy.static_data.equals(original_pool.static_data)

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": "FAKE_PATTERN"}),
            ("state", {"health_state": "FAKE_PATTERN"}),
            ("interval", {"medication": "FAKE_PATTERN"}),
        ],
    )
    def test_filter_no_matching_pattern_criterion_sequence_level(
        self, sequence_pools, pool_type, pattern
    ):
        """
        Test filtering with pattern criterion at sequence level that doesn't match any data.
        Should return an empty dataframe.
        """
        original_pool = sequence_pools[pool_type]
        criterion = PatternCriterion(pattern=pattern, contains=True)

        # -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            criterion, level="sequence", inplace=False
        )
        ## -- test
        assert filtered_pool_non_inplace.sequence_data.empty
        assert filtered_pool_non_inplace.static_data.empty

        # -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(criterion, level="sequence", inplace=True)

        ## -- test
        assert pool_copy.sequence_data.empty
        assert pool_copy.static_data.empty

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": ["EMERGENCY", "CONSULTATION"]}),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_which_pattern_criterion(
        self, sequence_pools, pool_type, pattern, snapshot
    ):
        """Test which method for pattern criterion"""
        pool = sequence_pools[pool_type]
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)
        matching_ids = pool.which(pattern_criterion)
        assert isinstance(matching_ids, set)
        snapshot.assert_match(sorted(matching_ids))

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": ["EMERGENCY", "CONSULTATION"]}),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_filter_sequence_level_consistency(
        self, sequence_pools, pool_type, pattern
    ):
        """
        Check consistency between filtering (inplace/non inplace) and which method.
        """
        original_pool = sequence_pools[pool_type]
        criterion = PatternCriterion(pattern=pattern, contains=True)

        # -- non inplace
        filtered_pool_non_inplace = original_pool.filter(
            criterion, level="sequence", inplace=False
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # -- inplace
        pool_copy = original_pool.copy()
        pool_copy.filter(criterion, level="sequence", inplace=True)
        inplace_result = pool_copy.sequence_data

        ## -- which
        matching_ids = sorted(list(original_pool.which(criterion)))

        ## -- test
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids

    @pytest.mark.parametrize(
        "pool_type,pattern",
        [
            ("event", {"event_type": ["EMERGENCY", "CONSULTATION"]}),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_pattern_sequence_filtering_via_dict_criterion(
        self, sequence_pools, pool_type, pattern
    ):
        """
        Verify consistency of sequence filtering using criterion defined in a dictionary.
        """
        original_pool = sequence_pools[pool_type]
        criterion = {"pattern": pattern, "contains": True}

        # -- non inplace filtering
        filtered_pool_non_inplace = original_pool.filter(
            criterion=criterion,
            criterion_type="pattern",
            level="sequence",
            inplace=False,
        )
        non_inplace_result = filtered_pool_non_inplace.sequence_data

        # -- inplace filtering
        pool_copy = original_pool.copy()
        pool_copy.filter(
            criterion=criterion,
            criterion_type="pattern",
            level="sequence",
            inplace=True,
        )
        inplace_result = pool_copy.sequence_data

        # -- determine matching IDs
        matching_ids = sorted(
            original_pool.which(
                criterion=criterion,
                criterion_type="pattern",
            )
        )

        # -- assertions
        assert non_inplace_result.equals(inplace_result)
        assert sorted(non_inplace_result.index.unique()) == matching_ids
        assert sorted(inplace_result.index.unique()) == matching_ids
