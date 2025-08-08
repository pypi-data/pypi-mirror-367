#!/usr/bin/env python3
"""
Test time criterion applied to sequence pools.
"""

import pytest

from tanat.criterion.mixin.time.settings import TimeCriterion


class TestTimeCriterion:
    """
    Tests for filtering sequence pools using time criterion.
    """

    @pytest.mark.parametrize(
        "pool_type,inplace,duration_within",
        [
            ("event", False, False),
            ("event", True, False),
            ("event", False, True),
            ("event", True, True),
            ("interval", False, False),
            ("interval", True, False),
            ("interval", False, True),
            ("interval", True, True),
        ],
    )
    def test_filter_entity_level_duration_within(
        self, sequence_pools, pool_type, inplace, duration_within, snapshot
    ):
        """
        Test filtering on entity level with duration_within.
        Tests strict containment vs partial overlap.
        """
        pool = sequence_pools[pool_type]
        if inplace:
            pool = pool.copy()

        time_criterion = TimeCriterion(
            start_after="2023-04-01",
            end_before="2023-05-01",
            duration_within=duration_within,
        )

        if inplace:
            pool_copy = pool.copy()
            result = pool_copy.filter(time_criterion, level="entity", inplace=True)
            assert result is None
            assert pool_copy.static_data.equals(pool.static_data)
            filtered_result = pool_copy.sequence_data
        else:
            filtered_pool = pool.filter(time_criterion, level="entity", inplace=False)
            assert filtered_pool is not pool
            filtered_result = filtered_pool.sequence_data

        snapshot.assert_match(filtered_result.to_csv())

    @pytest.mark.parametrize(
        "pool_type,inplace,sequence_within",
        [
            ("event", False, False),
            ("event", True, False),
            ("event", False, True),
            ("event", True, True),
            ("interval", False, False),
            ("interval", True, False),
            ("interval", False, True),
            ("interval", True, True),
            ("state", False, False),
            ("state", True, False),
            ("state", False, True),
            ("state", True, True),
        ],
    )
    def test_filter_sequence_level_sequence_within(
        self, sequence_pools, pool_type, inplace, sequence_within, snapshot
    ):
        """
        Test filtering on sequence level with sequence_within.
        Tests strict containment vs partial overlap.
        """
        pool = sequence_pools[pool_type]
        if inplace:
            pool = pool.copy()

        time_criterion = TimeCriterion(
            start_after="2023-04-01",
            end_before="2023-04-15",
            sequence_within=sequence_within,
        )

        if inplace:
            result = pool.filter(time_criterion, level="sequence", inplace=True)
            assert result is None
            filtered_seq_data = pool.sequence_data
            filtered_static_data = pool.static_data
        else:
            filtered_pool = pool.filter(time_criterion, level="sequence", inplace=False)
            assert filtered_pool is not pool
            filtered_seq_data = filtered_pool.sequence_data
            filtered_static_data = filtered_pool.static_data

        snapshot.assert_match(filtered_seq_data.to_csv())
        snapshot.assert_match(filtered_static_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,duration_within,sequence_within",
        [
            ("event", False, False),
            ("event", True, False),
            ("event", False, True),
            ("event", True, True),
            ("interval", False, False),
            ("interval", True, False),
            ("interval", False, True),
            ("interval", True, True),
            ("state", False, False),
            ("state", True, False),
            ("state", False, True),
            ("state", True, True),
        ],
    )
    def test_combined_duration_and_sequence_within_sequence_level(
        self, sequence_pools, pool_type, duration_within, sequence_within, snapshot
    ):
        """
        Combine duration_within and sequence_within filtering on sequence level.
        """
        pool = sequence_pools[pool_type]
        time_criterion = TimeCriterion(
            start_after="2023-01-01",
            end_before="2023-10-01",
            duration_within=duration_within,
            sequence_within=sequence_within,
        )

        filtered_pool = pool.filter(time_criterion, level="sequence", inplace=False)
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    def test_state_pool_entity_level_error(self, sequence_pools):
        """
        Ensure entity-level filtering raises error for state pools.
        """
        state_pool = sequence_pools["state"]

        for duration_within in [False, True]:
            for sequence_within in [False, True]:
                time_criterion = TimeCriterion(
                    start_after="2023-04-01",
                    end_before="2023-05-01",
                    duration_within=duration_within,
                    sequence_within=sequence_within,
                )

                with pytest.raises(NotImplementedError):
                    state_pool.filter(time_criterion, level="entity", inplace=False)
                with pytest.raises(NotImplementedError):
                    state_pool.filter(time_criterion, level="entity", inplace=True)

    def test_time_sequence_filtering_via_dict_criterion(self, sequence_pools, snapshot):
        """
        Validate filtering using dict-form criterion.
        """
        pool = sequence_pools["event"]
        time_criterion = {
            "start_after": "2023-04-01",
            "end_before": "2023-04-20",
        }

        filtered_pool = pool.filter(
            time_criterion, criterion_type="time", level="sequence", inplace=False
        )
        snapshot.assert_match(filtered_pool.sequence_data.to_csv())
        snapshot.assert_match(filtered_pool.static_data.to_csv())

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_which_time_criterion(self, sequence_pools, pool_type, snapshot):
        """Test which method for time criterion"""
        pool = sequence_pools[pool_type]
        time_criterion = TimeCriterion(
            start_after="2023-04-01", end_before="2023-05-01"
        )
        matching_ids = pool.which(time_criterion)
        assert isinstance(matching_ids, set)
        snapshot.assert_match(sorted(matching_ids))
