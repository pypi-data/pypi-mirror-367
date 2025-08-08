"""
Time criterion
==================

Filtering sequences or entities based on temporal constraints.
"""

# %% [markdown]
# ### Required imports

# %%
from datetime import datetime, timedelta

# Data simulation
from tanat.dataset.simulation.sequence import generate_event_sequences

# Sequence pools
from tanat.sequence import EventSequencePool

# Trajectory pools
from tanat.trajectory import TrajectoryPool

# Time-based filtering criterion
from tanat.criterion import TimeCriterion

# %% [markdown]
# ## 1. Data Setup
#
# Generate a simple sequence dataset with timestamps.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [12, 15, 20, 25]  # Varying sequence lengths
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
simple_pool.sequence_data

# %% [markdown]
# ## 2. Entity level filtering
#
# Filter entities (i.e., events) occurring within a specific time window.

# Between 3 months ago and now
start_date = datetime.now() - timedelta(days=90)
end_date = datetime.now()

time_window_criterion = TimeCriterion(
    start_after=start_date,
    end_before=end_date,
)

filtered_seqpool = simple_pool.filter(time_window_criterion, level="entity")
filtered_seqpool

# %%
# Filter a single sequence at entity level
single_seq = simple_pool["seq-1"]
filtered_seq = single_seq.filter(time_window_criterion)

filtered_seq

# %% [markdown]
# ## 3. Sequence level filtering

# Keep only sequences where **all events** fall within the time window.

# %%
time_window_criterion = TimeCriterion(
    start_after=start_date,
    end_before=end_date,
    # True: Sequence must be entirely contained within the time range
    sequence_within=True,
)
filtered_seqpool = simple_pool.filter(time_window_criterion, level="sequence")
filtered_seqpool

# %%
# Check if a single sequence fully matches the time window
single_seq = simple_pool["seq-0"]
matches = single_seq.match(time_window_criterion)

matches

# %%
# Get IDs of sequences matching the time criterion
matching_ids = simple_pool.which(time_window_criterion)
matching_ids

# %% [markdown]
# ## 4. Applying time criterion in a trajectory Pool
#
# Time criterion cannot be applied directly at the trajectory level,
# but can be applied to sequences or entities inside trajectories through filtering.

# %%
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")

# %%
# Filter entities inside trajectories
filtered_trajpool = trajectory_pool.filter(
    time_window_criterion,
    level="entity",
    sequence_name="events",  # Specify which sequence to filter
)

filtered_trajpool

# %%
# Filter entire sequences inside trajectories
filtered_trajpool = trajectory_pool.filter(
    time_window_criterion,
    level="sequence",
    sequence_name="events",
    intersection=True,  # Propagate sequence filtering to trajectory level
)

filtered_trajpool
