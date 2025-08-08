#!/usr/bin/env python3
"""
Test time criterion applied to a single sequence.
"""

import pytest

from tanat.criterion.mixin.time.settings import TimeCriterion


class TestTimeCriterion:
    """
    Test the time match method applied to individual sequence.
    """

    @pytest.mark.parametrize(
        "pool_type,sequence_id,start_after,end_before,expected_result",
        [
            ("event", 1, "2023-01-01", "2023-02-01", True),
            ("event", 1, "2018-03-01", "2018-03-10", False),
            ("interval", 3, "2023-04-01", "2023-05-01", True),
            ("interval", 3, "2018-03-01", "2018-03-10", False),
            ("state", 4, "2023-06-01", "2023-08-01", True),
            ("state", 4, "2018-01-01", "2018-06-01", False),
        ],
    )
    def test_match_duration_within_true(
        self,
        sequence_pools,
        pool_type,
        sequence_id,
        start_after,
        end_before,
        expected_result,
    ):
        """
        Test sequence.match with duration_within=True (object + dict).
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion_obj = TimeCriterion(
            start_after=start_after,
            end_before=end_before,
            duration_within=True,
        )
        assert sequence.match(criterion_obj) == expected_result

        criterion_dict = {
            "start_after": start_after,
            "end_before": end_before,
            "duration_within": True,
        }
        assert sequence.match(criterion_dict, criterion_type="time") == expected_result

    @pytest.mark.parametrize(
        "pool_type,sequence_id,start_after,end_before,expected_result",
        [
            ("event", 1, "2023-01-01", "2023-02-01", True),
            ("event", 1, "2018-03-01", "2018-03-10", False),
            ("interval", 3, "2023-04-01", "2023-04-20", True),
            ("interval", 3, "2018-03-01", "2018-03-10", False),
            ("state", 4, "2023-06-01", "2023-03-01", True),
            ("state", 4, "2018-01-01", "2018-06-01", False),
        ],
    )
    def test_match_duration_within_false(
        self,
        sequence_pools,
        pool_type,
        sequence_id,
        start_after,
        end_before,
        expected_result,
    ):
        """
        Test sequence.match with duration_within=False (object + dict).
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion_obj = TimeCriterion(
            start_after=start_after,
            end_before=end_before,
            duration_within=False,
        )
        assert sequence.match(criterion_obj) == expected_result

        criterion_dict = {
            "start_after": start_after,
            "end_before": end_before,
            "duration_within": False,
        }
        assert sequence.match(criterion_dict, criterion_type="time") == expected_result

    @pytest.mark.parametrize(
        "pool_type,sequence_id,start_after,end_before,expected_result",
        [
            ("event", 4, "2023-01-01", "2023-10-01", True),
            ("event", 4, "2023-01-01", "2023-04-01", False),
            ("interval", 6, "2023-03-01", "2023-08-01", True),
            ("interval", 6, "2023-03-01", "2023-04-01", False),
            ("state", 3, "2022-12-01", "2024-01-01", True),
            ("state", 3, "2018-03-01", "2018-03-10", False),
        ],
    )
    def test_match_sequence_within_true(
        self,
        sequence_pools,
        pool_type,
        sequence_id,
        start_after,
        end_before,
        expected_result,
    ):
        """
        Test sequence.match with sequence_within=True (object + dict).
        Tests strict containment - entire sequence must be within time range.
        """
        pool = sequence_pools[pool_type]
        sequence = pool[sequence_id]

        criterion_obj = TimeCriterion(
            start_after=start_after,
            end_before=end_before,
            sequence_within=True,
        )
        assert sequence.match(criterion_obj) == expected_result

        criterion_dict = {
            "start_after": start_after,
            "end_before": end_before,
            "sequence_within": True,
        }
        assert sequence.match(criterion_dict, criterion_type="time") == expected_result

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            (
                "event",
                1,
                {
                    "start_after": "2023-01-01",
                    "end_before": "2023-02-01",
                    "duration_within": True,
                },
            ),
            (
                "interval",
                3,
                {
                    "start_after": "2023-04-01",
                    "end_before": "2023-05-01",
                    "duration_within": True,
                },
            ),
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
        criterion = TimeCriterion(**criterion_kwargs)
        result = sequence.filter(criterion, inplace=True)

        assert result is None
        snapshot.assert_match(sequence.sequence_data.to_csv())

    @pytest.mark.parametrize(
        "pool_type,sequence_id,criterion_kwargs",
        [
            (
                "event",
                1,
                {
                    "start_after": "2023-01-01",
                    "end_before": "2023-02-01",
                    "duration_within": True,
                },
            ),
            (
                "interval",
                3,
                {
                    "start_after": "2023-04-01",
                    "end_before": "2023-05-01",
                    "duration_within": True,
                },
            ),
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
        criterion = TimeCriterion(**criterion_kwargs)
        print(sequence_copy)
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
        criterion_kwargs = {"start_after": "2023-04-01", "end_before": "2023-05-01"}
        criterion = TimeCriterion(**criterion_kwargs)

        with pytest.raises(NotImplementedError):
            sequence.filter(criterion)

        ## -- from dict
        with pytest.raises(NotImplementedError):
            sequence.filter(criterion_kwargs, criterion_type="time")
