"""
Query criterion
==================

Filtering sequences or entities based on pandas-like query logic.
"""

# %% [markdown]
# ### Required imports

# %%
# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
)

# Trajectory pools
from tanat.trajectory import (
    TrajectoryPool,
)

# Criterion
from tanat.criterion import (
    QueryCriterion,
)

# %% [markdown]
# ## 1. Data Setup
#
# Generate a simple sequence dataset to demonstrate filtering with query criterion.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate event sequences with predefined vocabulary
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

# %% [markdown]
# ## 2. Entity Level Filtering
#
# Filter entities inside sequences based on a query criterion.

# %%
criterion = QueryCriterion(query="event == 'A'")
filtered_seqpool = simple_pool.filter(criterion, level="entity")

filtered_seqpool

# %%
# Filter entities in a single sequence
single_seq = simple_pool["seq-0"]
criterion = QueryCriterion(query="event == 'A'")
filtered_seq = single_seq.filter(criterion)

filtered_seq

# %% [markdown]
# ## 3. Sequence Level Filtering
#
# Filter entire sequences that match the query criterion.

# %%
criterion = QueryCriterion(query="event == 'A'")
filtered_seqpool = simple_pool.filter(criterion, level="sequence")

filtered_seqpool

# %%
# Check if a single sequence matches the criterion
single_seq = simple_pool["seq-0"]
criterion = QueryCriterion(query="event == 'A'")
matches = single_seq.match(criterion)

matches

# %%
# Get IDs of sequences matching the criterion
criterion = QueryCriterion(query="event == 'A'")
matching_ids = simple_pool.which(criterion)

matching_ids

# %% [markdown]
# ## 4. Applying query criterion in a trajectory Pool
#
# Query criterion cannot be applied directly at the trajectory level,
# but can be applied to sequences or entities inside trajectories through filtering.

# %%
# Create an empty trajectory pool and add the event sequence pool
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")

# %%
# Filter sequences in the trajectory pool
criterion = QueryCriterion(query="event == 'A'")
filtered_trajpool = trajectory_pool.filter(
    criterion,
    level="sequence",
    # Specify which sequence to filter
    sequence_name="events",
    # Propagate filtered sequences to trajectory level (for multi-sequence trajectories)
    intersection=True,
)

filtered_trajpool

# %%
# Filter entities in the trajectory pool sequences
criterion = QueryCriterion(query="event == 'A'")
filtered_trajpool = trajectory_pool.filter(
    criterion,
    level="entity",
    sequence_name="events",  # Specify which sequence to filter
)

filtered_trajpool

# %%
# Filter entities in a single trajectory
criterion = QueryCriterion(query="event == 'A'")
single_trajectory = trajectory_pool["seq-0"]
filtered_traj = single_trajectory.filter(
    criterion,
    sequence_name="events",  # Specify which sequence to filter
)

filtered_traj
