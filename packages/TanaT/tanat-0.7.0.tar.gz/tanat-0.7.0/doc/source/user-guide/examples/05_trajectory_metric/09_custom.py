"""
Create Custom Metric
==================

Create a custom trajectory metric.
"""

# %% [markdown]
# ### Required imports

# %%
from datetime import datetime

# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
    generate_state_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
    StateSequencePool,
)

from tanat.trajectory import TrajectoryPool

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate the aggregation metric.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate simple sequences for clear metric demonstration
simple_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["A", "B", "C", "D"],
    missing_data=0.0,
    entity_feature="event",
    seed=SEED,
)

simple_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

simple_pool = EventSequencePool(simple_data, simple_settings)
simple_pool

# %%
# Generate another set of simple sequences (states)
simple_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["Z", "Y", "X", "W"],
    missing_data=0.0,
    entity_feature="states",
    seed=SEED,
)

simple_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "default_end_value": datetime.now(),  # Avoid warning
    "entity_features": ["states"],
}
simple_pool_2 = StateSequencePool(simple_data, simple_settings)
simple_pool_2

# %%
# Build trajectory pool
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")
trajectory_pool.add_sequence_pool(simple_pool_2, "states")

# Configure settings
trajectory_pool.update_settings(intersection=False)


# %% [markdown]
# ### Custom Trajectory Metric
#
# Define a dummy trajectory metric that consistently returns a fixed distance value between two trajectories.


# %%
# Create a custom trajectory metric
from tanat.metric.trajectory.base.metric import TrajectoryMetric
import dataclasses


@dataclasses.dataclass
class DummySettings:
    """Settings for the dummy metric."""

    value: int = 42  # distance value to return


class DummyTrajectoryMetric(TrajectoryMetric, register_name="dummy"):
    """Metric that computes a dummy distance between two trajectories."""

    SETTINGS_DATACLASS = DummySettings

    def __init__(self, settings=None):
        if settings is None:
            settings = DummySettings()
        super().__init__(settings)

    def __call__(self, seq_a, seq_b, **kwargs):
        """Calculate the length difference between two sequences."""
        with self.with_tmp_settings(**kwargs):  # Temporarily override settings
            return self.settings.value


# %%
# Access two simple trajectories
traj_1 = trajectory_pool["seq-0"]
traj_2 = trajectory_pool["seq-1"]

# Test custom metric
custom_metric = DummyTrajectoryMetric()
custom_metric(traj_1, traj_2)

# %%
custom_metric.collect_as_matrix(trajectory_pool)
