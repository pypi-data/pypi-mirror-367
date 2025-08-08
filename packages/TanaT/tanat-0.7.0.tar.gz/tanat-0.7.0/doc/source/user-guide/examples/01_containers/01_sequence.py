"""
Sequence container
==================

A sequence container allows storing and accessing sequence data.
"""

# %% [markdown]
# ### Required imports

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


# %% [markdown]
# ## 1. Event sequences
#
# Let's create a simple sequence of events data.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate simple sequences of events
simple_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["A", "B", "C", "D"],
    missing_data=0.0,
    entity_feature="event",
    seed=SEED,
)

# %%
# Store data in a sequence pool
simple_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

simple_pool = EventSequencePool(simple_data, simple_settings)
simple_pool

# %%
# Access single sequence
simple_pool["seq-0"]

# %%
# Access first entity (0-based)
simple_pool["seq-0"][0]


# %% [markdown]
# ## 2. States sequences
#
# Let's create a simple sequence of states data.


# %%
# Sequence of states
data_states = generate_state_sequences(
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
simple_pool = StateSequencePool(data_states, simple_settings)
simple_pool

# %%
# Access single sequence
simple_pool["seq-0"]


# %%
# Access first entity (0-based)
simple_pool["seq-0"][0]

# %% [markdown]
# ## 3. Intervals sequence
# Let's create a simple sequence of intervals data.

# %%
# Sequence of intervals
data_intervals = generate_interval_sequences(
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
    "end_column": "end_date",
    "entity_features": ["states"],
}
simple_pool = IntervalSequencePool(data_intervals, simple_settings)
simple_pool

# %%
# Access single sequence
simple_pool["seq-0"]


# %%
# Access first entity (0-based)
simple_pool["seq-0"][0]


# %% [markdown]
# ## 4. Transformations
# Transform sequences to different data representations.
# The following transformations are available for both sequence pools and individual sequence objects.

# %%
# Convert to occurrence data
occurrence_data = simple_pool.to_occurrence(by_id=True, drop_na=True)
occurrence_data

# %%
# Convert to occurrence frequency
frequency_data = simple_pool.to_occurrence_frequency(
    by_id=False,
    drop_na=True,
)
frequency_data

# %%
# Convert to relative time
relative_time_data = simple_pool.to_relative_time(
    drop_na=True,
    granularity="day",
)
relative_time_data

# %%
# Calculate time spent
time_spent_data = simple_pool.to_time_spent(
    by_id=True,
    granularity="day",
    drop_na=True,
)
time_spent_data

# %%
# Calculate relative rank
relative_rank_data = simple_pool.to_relative_rank(drop_na=True)
relative_rank_data

# %%
# Modify sequence starting point (t_zero)
simple_pool.zero_from_position(2)
updated_rank_data = simple_pool.to_relative_rank(drop_na=True)
updated_rank_data
