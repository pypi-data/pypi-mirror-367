"""
Hierarchical Clustering
=======================

This module demonstrates how to perform hierarchical clustering on both sequence pools and trajectory pools.
"""

# %% [markdown]
# ### Required Imports

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

# Clustering tools
from tanat.clustering import (
    HierarchicalClusterer,
    HierarchicalClustererSettings,
)

# %% [markdown]
# ## 1. Data Initialization and Generation
#
# We generate simple event sequences to use as input for clustering.

# %%
NUM_SEQUENCES = 10
SEQUENCE_LENGTHS = [4, 5, 6, 7, 8, 9, 10, 11, 12]
RANDOM_SEED = 42

# Generate synthetic event sequences
event_data = generate_event_sequences(
    n_seq=NUM_SEQUENCES,
    seq_size=SEQUENCE_LENGTHS,
    vocabulary=["A", "B", "C", "D"],
    missing_data=0.0,
    entity_feature="event",
    seed=RANDOM_SEED,
)

# Define event sequence settings
event_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

event_pool = EventSequencePool(event_data, event_settings)
event_pool


# %% [markdown]
# ## 2. Hierarchical Clustering on a Sequence Pool
#
# We cluster individual event sequences using a linear pairwise distance metric.

# %%
# Initialize the clusterer with default settings
hc_settings = HierarchicalClustererSettings(
    metric="linearpairwise",  # Sequence-level metric
    cluster_column="hclass",  # Column where cluster labels will be stored
)

clusterer = HierarchicalClusterer(settings=hc_settings)

# Show clusterer settings
clusterer.view_settings()

# %%
# Fit the clusterer on the sequence pool
clusterer.fit(event_pool)

# Show clustering summary
print(clusterer.summarize())


# %% [markdown]
# ## 3. Hierarchical Clustering on a Trajectory Pool
#
# Clustering entire trajectories using a trajectory-level metric (e.g., aggregation).

# %%
# Initialize and populate a trajectory pool
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(event_pool, "events")

# %%
# Configure a new clusterer for trajectory clustering
hc_settings = HierarchicalClustererSettings(
    metric="aggregation",  # Trajectory-level distance metric
    cluster_column="hclass",  # Cluster labels stored here
)

clusterer = HierarchicalClusterer(settings=hc_settings)

# Fit the clusterer on the trajectory pool
clusterer.fit(trajectory_pool)

# Summarize results
print(clusterer.summarize())

# %%
# Access clustering results from the static data
trajectory_pool.static_data
