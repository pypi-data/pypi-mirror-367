"""
Pattern criterion
==================

Filtering sequences or entities based on event patterns.
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

# Pattern-based filtering criterion
from tanat.criterion import PatternCriterion

# %% [markdown]
# ## 1. Data Setup
#
# Generate a simple sequence dataset for pattern-based filtering.

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
# ## 2. Entity level filtering
#
# Filter entities that are part of a specific event pattern.

# %%
# Example: look for sequences containing the pattern A → B → C
pattern_criterion = PatternCriterion(
    pattern={"event": ["A", "B", "C"]},
    contains=True,  # Match anywhere in the sequence (not necessarily the full sequence)
)

filtered_seqpool = simple_pool.filter(pattern_criterion, level="entity")
filtered_seqpool

# %%
# Filter a single sequence at entity level
single_seq = simple_pool["seq-5"]
filtered_seq = single_seq.filter(pattern_criterion)

filtered_seq

# %% [markdown]
# ## 3. Sequence level filtering
#
# Keep only sequences that match the full pattern.

# %%
filtered_seqpool = simple_pool.filter(pattern_criterion, level="sequence")
filtered_seqpool

# %%
# Check if a single sequence matches the pattern
single_seq = simple_pool["seq-5"]
matches = single_seq.match(pattern_criterion)

matches

# %%
# Get IDs of sequences matching the pattern
matching_ids = simple_pool.which(pattern_criterion)
matching_ids

# %% [markdown]
# ## 4. Applying pattern criterion in a trajectory pools
#
# Pattern criterion cannot be applied directly at the trajectory level,
# but can be applied to sequences or entities inside trajectories through filtering.

# %%
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")

# %%
# Filter entities in trajectories based on pattern
filtered_trajpool = trajectory_pool.filter(
    pattern_criterion,
    level="entity",
    sequence_name="events",  # Specify which sequence to filter
)

filtered_trajpool

# %%
# Filter full sequences in trajectories based on pattern
filtered_trajpool = trajectory_pool.filter(
    pattern_criterion,
    level="sequence",
    sequence_name="events",
    intersection=True,  # Propagate filtered sequences to the trajectory level
)

filtered_trajpool
