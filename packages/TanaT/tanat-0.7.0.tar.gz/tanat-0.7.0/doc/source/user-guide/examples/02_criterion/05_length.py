"""
Length criterion
==================

Filtering sequences based on their length.
"""

# %% [markdown]
# ### Required imports

# %%
# Data simulation
from tanat.dataset.simulation.sequence import generate_event_sequences

# Sequence pools
from tanat.sequence import EventSequencePool

# Trajectory pools
from tanat.trajectory import TrajectoryPool

# Length-based filtering criterion
from tanat.criterion import LengthCriterion

# %% [markdown]
# ## 1. Data Setup
#
# Generate a simple sequence dataset with varying lengths.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

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

# %% [markdown]
# ## 2. Sequence level filtering
#
# Keep only sequences whose length satisfies the criterion.

# %%
# Example: keep sequences with length strictly greater than 5
length_criterion = LengthCriterion(gt=5)
filtered_seqpool = simple_pool.filter(length_criterion)
filtered_seqpool

# %%
# Check if a single sequence matches the length criterion
single_seq = simple_pool["seq-0"]
matches = single_seq.match(length_criterion)
matches

# %%
# Get IDs of sequences matching the length criterion
matching_ids = simple_pool.which(length_criterion)
matching_ids

# %% [markdown]
# ## 3. Applying length criterion in a trajectory pool
#
# Length criterion are applied at the sequence level inside trajectory pools.

# %%
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")

# %%
# Filter sequences in trajectories based on length
filtered_trajpool = trajectory_pool.filter(
    length_criterion,
    level="sequence",
    sequence_name="events",  # Specify which sequence to filter
)

filtered_trajpool
