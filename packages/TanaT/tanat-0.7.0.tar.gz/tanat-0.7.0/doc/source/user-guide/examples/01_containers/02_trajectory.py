"""
Trajectory Container
====================

A trajectory container stores and provides access to trajectory data.
Trajectories combine multiple sequence types, such as events, states, and intervals.
"""

# %% [markdown]
# ### Required Imports


# %%
from datetime import datetime

# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
    generate_state_sequences,
    generate_interval_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
    StateSequencePool,
    IntervalSequencePool,
)

# Trajectory pool
from tanat.trajectory import TrajectoryPool

# %% [markdown]
# ## 1. Data Setup
#

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate simple event sequences
event_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["A", "B", "C", "D"],
    missing_data=0.0,
    entity_feature="event",
    seed=SEED,
)

# Event sequence pool settings
event_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

event_pool = EventSequencePool(event_data, event_settings)
event_pool


# %%
# Generate interval sequences
interval_data = generate_interval_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["Z", "Y", "X", "W"],
    missing_data=0.0,
    entity_feature="states",
    seed=SEED,
)

interval_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "end_column": "end_date",
    "entity_features": ["states"],
}
interval_pool = IntervalSequencePool(interval_data, interval_settings)
interval_pool

# %%
# Generate state sequences
state_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["Z", "Y", "X", "W"],
    missing_data=0.0,
    entity_feature="states",
    seed=SEED,
)

state_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "default_end_value": datetime.now(),  # Avoid warning
    "entity_features": ["states"],
}

state_pool = StateSequencePool(state_data, state_settings)
state_pool

# %% [markdown]
# ## 2. Build Trajectory Pool

# %%
# Build trajectory pool
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(event_pool, "events")
trajectory_pool.add_sequence_pool(state_pool, "states")
trajectory_pool.add_sequence_pool(interval_pool, "intervals")

# Update trajectory settings
trajectory_pool.update_settings(intersection=False)

# View trajectory pool
trajectory_pool


# %%
# Access trajectory by id
target_id = "seq-0"
trajectory_pool[target_id]  # return all sub-sequences in the trajectory

# %%
# Access sub-sequence
trajectory_pool[target_id]["events"]
trajectory_pool[target_id]["states"]
trajectory_pool[target_id]["intervals"]

# %%
# Access sequence pool within trajectory
trajectory_pool.sequence_pools["events"]
