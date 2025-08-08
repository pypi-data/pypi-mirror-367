#!/usr/bin/env python3
"""
Test pattern criterion applied to trajectory pools.
"""

import pytest

from tanat.criterion.mixin.pattern.settings import PatternCriterion
from tanat.criterion.mixin.pattern.exception import InvalidColumnPatternError
from tanat.criterion.base.exception import InvalidCriterionError


class TestPatternCriterion:
    """
    Test pattern criterion applied to trajectory pools.
    """

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("state", {"health_state": "TREATMENT"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_trajectories_on_sequence_level(
        self, trajectory_pool, sequence_name, pattern, snapshot
    ):
        """
        Trajectory pool: Pattern criterion applied to sequence level (inplace=False).
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)
        filtered_pool = trajectory_pool.filter(
            criterion=pattern_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))
        assert filtered_pool.settings.intersection is True

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_trajectories_on_entity_level(
        self, trajectory_pool, sequence_name, pattern, snapshot
    ):
        """
        Test filtering trajectories on entity level.
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)
        filtered_pool = trajectory_pool.filter(
            criterion=pattern_criterion,
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
        criterion = PatternCriterion(
            pattern={"health_state": "TREATMENT"}, contains=True
        )
        with pytest.raises(NotImplementedError):
            trajectory_pool.filter(
                criterion=criterion,
                level="entity",
                sequence_name="state",
                inplace=False,
                intersection=True,
            )

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("state", {"health_state": "TREATMENT"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_trajectories_on_sequence_level_inplace(
        self, trajectory_pool, sequence_name, pattern, snapshot
    ):
        """
        Trajectory pool: Pattern criterion applied to sequence level (inplace=True).
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        ## -- filtering on copy
        trajectory_pool_copy = trajectory_pool.copy()
        filtered_pool = trajectory_pool_copy.filter(
            criterion=pattern_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        ## -- inplace should return None
        assert filtered_pool is None
        snapshot.assert_match(sorted(trajectory_pool_copy.unique_ids))

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("state", {"health_state": "TREATMENT"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_trajectories_on_sequence_level_consistency(
        self, trajectory_pool, sequence_name, pattern
    ):
        """
        Check filter sequence level with inplace=True and inplace=False produce the same results.
        """
        ## -- pattern criterion
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=pattern_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        non_inplace_result = sorted(filtered_pool.unique_ids)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=pattern_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": ["EMERGENCY", "SPECIALIST"]}),
            ("state", {"health_state": ["TREATMENT", "CONVALESCENCE"]}),
            ("interval", {"medication": ["ANTIBIOTIC", "PAIN_RELIEVER"]}),
        ],
    )
    def test_filter_trajectories_with_multiple_patterns(
        self, trajectory_pool, sequence_name, pattern, snapshot
    ):
        """
        Test filtering with multiple patterns in the criterion.
        """
        ## -- pattern criterion with multiple patterns
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=pattern_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )
        snapshot.assert_match(sorted(filtered_pool.unique_ids))

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "NONEXISTENT_EVENT"}),
            ("state", {"health_state": "NONEXISTENT_STATE"}),
            ("interval", {"medication": "NONEXISTENT_MEDICATION"}),
        ],
    )
    def test_filter_no_matching_pattern_criterion(
        self, trajectory_pool, sequence_name, pattern
    ):
        """
        Test filtering with pattern criterion that doesn't match any data.
        Should return an empty trajectory pool.
        """
        ## -- pattern criterion with non-existent pattern
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Non-inplace filtering
        filtered_pool = trajectory_pool.filter(
            criterion=pattern_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=False,
            intersection=True,
        )

        assert filtered_pool.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "NONEXISTENT_EVENT"}),
            ("state", {"health_state": "NONEXISTENT_STATE"}),
            ("interval", {"medication": "NONEXISTENT_MEDICATION"}),
        ],
    )
    def test_filter_no_matching_pattern_criterion_inplace(
        self, trajectory_pool, sequence_name, pattern
    ):
        """
        Test filtering with pattern criterion that doesn't match any data (inplace=True).
        Should result in an empty trajectory pool.
        """
        ## -- pattern criterion with non-existent pattern
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Inplace filtering
        traj_pool_copy = trajectory_pool.copy()
        traj_pool_copy.filter(
            criterion=pattern_criterion,
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )

        # Test empty result
        assert traj_pool_copy.unique_ids == set()

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"NONEXISTENT_COLUMN": "EMERGENCY"}),
            ("state", {"NONEXISTENT_COLUMN": "TREATMENT"}),
            ("interval", {"NONEXISTENT_COLUMN": "ANTIBIOTIC"}),
        ],
    )
    def test_filter_invalid_column_name(self, trajectory_pool, sequence_name, pattern):
        """
        Test filtering with pattern criterion that has an invalid column name.
        Should raise InvalidColumnPatternError.
        """
        ## -- pattern criterion with invalid column name
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)

        # Check both inplace=False and inplace=True
        with pytest.raises(InvalidColumnPatternError):
            trajectory_pool.filter(
                criterion=pattern_criterion,
                level="sequence",
                sequence_name=sequence_name,
                inplace=False,
                intersection=True,
            )

        traj_pool_copy = trajectory_pool.copy()
        with pytest.raises(InvalidColumnPatternError):
            traj_pool_copy.filter(
                criterion=pattern_criterion,
                level="sequence",
                sequence_name=sequence_name,
                inplace=True,
                intersection=True,
            )

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("state", {"health_state": "TREATMENT"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_pattern_filtering_via_dict_criterion(
        self, trajectory_pool, sequence_name, pattern
    ):
        """
        Verify consistency of filtering using criterion defined in a dictionary.
        """
        # Dictionary criterion
        dict_criterion = {"pattern": pattern, "contains": True}

        # Non-inplace filtering with dict criterion
        filtered_pool = trajectory_pool.filter(
            criterion=dict_criterion,
            criterion_type="pattern",
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
            criterion_type="pattern",
            level="sequence",
            sequence_name=sequence_name,
            inplace=True,
            intersection=True,
        )
        inplace_result = sorted(traj_pool_copy.unique_ids)

        # Test consistency
        assert non_inplace_result == inplace_result

    @pytest.mark.parametrize(
        "sequence_name,pattern",
        [
            ("event", {"event_type": "EMERGENCY"}),
            ("state", {"health_state": "TREATMENT"}),
            ("interval", {"medication": "ANTIBIOTIC"}),
        ],
    )
    def test_intersection_false(
        self, trajectory_pool, sequence_name, pattern, snapshot
    ):
        """
        Test that setting intersection=False does not affect the length of the filtered
        trajectory pool, but does affect the length of the inner sequence pool.
        """
        pattern_criterion = PatternCriterion(pattern=pattern, contains=True)
        filtered_pool = trajectory_pool.filter(
            criterion=pattern_criterion,
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
        Which method should raise an error for pattern criterion because this criterion is not
        applicable at 'trajectory' level.
        """

        criterion_kwargs = {"pattern": {"FAKE_COLUMN": "dummy_pattern"}}
        criterion = PatternCriterion(**criterion_kwargs)

        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion)

        ## -- from dict
        with pytest.raises(InvalidCriterionError):
            trajectory_pool.which(criterion_kwargs, criterion_type="pattern")
