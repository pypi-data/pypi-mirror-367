"""
Static criterion
==================

Filtering sequences based on pandas-like queries applied to static data.
"""

# %% [markdown]
# ### Required imports

# %%
import pandas as pd
import numpy as np

# Data simulation
from tanat.dataset.simulation.sequence import generate_event_sequences

# Sequence pools
from tanat.sequence import EventSequencePool

# Trajectory pools
from tanat.trajectory import TrajectoryPool

# Static filtering criterion
from tanat.criterion import StaticCriterion

# %% [markdown]
# ## 1. Data Setup
#
# Generate a simple sequence dataset and associated static data for filtering.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate sequences with fixed vocabulary
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

# %%
# Generate static data (e.g., demographic info) matching the sequence IDs
ids = list(simple_pool.unique_ids)
static_df = pd.DataFrame(
    {
        "id": ids,
        # age between 20 and 60
        "age": np.random.randint(20, 60, size=len(ids)),
        # score between 0 and 100
        "score": np.round(np.random.uniform(0, 100, len(ids)), 2),
    }
)

# Attach static data to the sequence pool
simple_pool.add_static_features(static_df)

# %% [markdown]
# ## 2. Sequence level filtering
#
# Filter sequences based on static attributes.

# %%
criterion = StaticCriterion(query="age > 40")
filtered_seqpool = simple_pool.filter(criterion)

filtered_seqpool

# %%
# Check if a single sequence matches the static criterion
single_seq = simple_pool["seq-0"]
criterion = StaticCriterion(query="age > 40")
matches = single_seq.match(criterion)

matches

# %%
# Get IDs of sequences matching the static criterion
criterion = StaticCriterion(query="age > 40")
matching_ids = simple_pool.which(criterion)

matching_ids

# %% [markdown]
# ## 3. Trajectory level filtering
#
# Filter trajectories based on static attributes linked to their sequences.

# %%
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")

# Attach static data to the trajectory pool
trajectory_pool.add_static_features(static_df, id_column="id")

# %%
# Filter trajectories
criterion = StaticCriterion(query="age > 40")
filtered_trajpool = trajectory_pool.filter(criterion, level="trajectory")

filtered_trajpool

# %%
# Check if a single trajectory matches the static criterion
single_traj = trajectory_pool["seq-0"]
criterion = StaticCriterion(query="age > 40")
matches = single_traj.match(criterion)

matches

# %%
# Get IDs of trajectories matching the static criterion
criterion = StaticCriterion(query="age > 40")
matching_ids = trajectory_pool.which(criterion)

matching_ids
