"""
Aggregation Trajectory Metric
==================

Compute the aggregated distance between two trajectories.
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

# Sequence Metrics
from tanat.metric.trajectory import (
    AggregationTrajectoryMetric,
    AggregationTrajectoryMetricSettings,
)

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
# ### Aggregation Trajectory Metric
#
# Aggregation trajectory metric computes a distance between two trajectories.

# %%
# Create aggregation metric
settings = AggregationTrajectoryMetricSettings()
mean_agg_metric = AggregationTrajectoryMetric(settings=settings)

# -- Settings overview
mean_agg_metric.view_settings()

# %% [markdown]
# By default the aggregation metric computes linear pairwise distance between sequences before aggregating.
# Mean aggregation is used as default.

# %%
# Access two simple trajectories
traj_1 = trajectory_pool["seq-0"]
traj_2 = trajectory_pool["seq-1"]

# Compute aggregated distance
mean_agg_metric(traj_1, traj_2)

# %%
# Compute mean aggregation directly on trajectory pool
mean_agg_metric.collect_as_matrix(trajectory_pool)

# %% [markdown]
# Before computing the metric, you can customize its behavior using `update_settings()` or `kwargs`.

# %%
# Preconfigure the the behavior of the metric
mean_agg_metric.update_settings(
    # Compute DTW distance before aggregating
    metric_mapper={"default_metric": "dtw"},
)

mean_agg_metric.collect_as_matrix(trajectory_pool)

# %%
# Modify the behavior directly from kwargs
mean_agg_metric.collect_as_matrix(
    trajectory_pool,
    # Compute DTW distance before aggregating
    metric_mapper={"default_metric": "dtw"},
)
