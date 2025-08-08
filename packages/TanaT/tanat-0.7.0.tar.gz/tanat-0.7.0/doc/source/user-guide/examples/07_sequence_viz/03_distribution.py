"""
Distribution Visualization
==========================

This module demonstrates how to visualize sequence data using distribution plots.
Distribution visualization shows the proportion of different states over time,
inspired by the State Sequence Distribution plots from TraMineR.

**Important Note**: Distribution visualizations are specifically designed for
**STATE SEQUENCES ONLY**. They analyze how states are distributed across time
periods and are not applicable to event or interval sequences.
"""

# %% [markdown]
# ### Required Imports

# %%
from datetime import datetime

# Data access and simulation
from tanat.dataset import access
from tanat.dataset.simulation.sequence import generate_state_sequences

# Sequence pool
from tanat.sequence import StateSequencePool, StateSequenceSettings

# Distribution visualization
from tanat.visualization.sequence import SequenceVisualizer

# %% [markdown]
# ## 1. Real-World Data: MVAD Dataset
#
# We'll start with the MVAD (Multichannel Visualization and Analysis of Data) dataset,
# a well-known dataset in sequence analysis that shows transition from school to work
# for young adults. This creates a "classic" state distribution visualization.
#
# **Key Point**: MVAD is a state sequence dataset - perfect for distribution analysis!

# %%
# Load the MVAD dataset
mvad_data = access("mvad")
print("MVAD dataset overview:")
print(mvad_data.head(10))
print(f"Dataset shape: {mvad_data.shape}")
print(f"Unique states: {mvad_data['value'].unique()}")

# %%
# Initialize MVAD as a state sequence pool
mvad_settings = StateSequenceSettings(
    id_column="id",
    start_column="start",
    end_column="end",
    entity_features=["value"],
)

mvad_pool = StateSequencePool(sequence_data=mvad_data, settings=mvad_settings)
print(f"Number of sequences: {len(mvad_pool.unique_ids)}")
mvad_pool

# %% [markdown]
# ## 2. Creating "classic" State Distribution Plots
#
# The distribution visualization creates a stacked area plot showing the proportion
# of each state over time - this is the "classic" state distribution plot commonly used
# in sequence analysis.
#
# **This visualization answers**: "At each time point, what percentage of individuals
# are in each state?"

# %%
# Basic MVAD distribution plot

# This shows the proportion of each state over time
# fmt: off
SequenceVisualizer.distribution(granularity="day") \
    .colors("Set1") \
    .title("MVAD State Distribution Over Time") \
    .legend(show=True, loc="upper right") \
    .x_axis(label="Time") \
    .y_axis(label="State Proportion") \
    .draw(mvad_pool)
# fmt: on

# %% [markdown]
# ## 3. Distribution Types
#
# Distribution visualizations can show different types of aggregations:
# percentage, count, or proportion.

# %%
# Count distribution instead of percentage

# This shows the absolute count of individuals in each state over time
# fmt: off
SequenceVisualizer.distribution(
    distribution_type="count", 
    granularity="day"
) \
    .colors("Set1") \
    .title("MVAD State Counts Over Time") \
    .legend(show=True, title="States") \
    .draw(mvad_pool)
# fmt: on

# %%
# Proportion distribution (0-1 scale instead of 0-100)

# This shows the proportion of individuals in each state at each time point
# fmt: off
SequenceVisualizer.distribution(
    distribution_type="proportion",
    granularity="day"
) \
    .colors("Paired") \
    .title("MVAD State Proportions (0-1 scale)") \
    .legend(show=True) \
    .draw(mvad_pool)
# fmt: on

# %% [markdown]
# ## 4. Unstacked Distributions
#
# For better comparison between states, we can create unstacked line plots.

# %%
# Unstacked distribution - separate lines for each state

# This shows each state as a separate line, useful for comparing trends
# fmt: off
SequenceVisualizer.distribution(
    distribution_type="percentage",
    stacked=False,
    granularity="day"
) \
    .colors("tab10") \
    .title("MVAD State Evolution (Unstacked)") \
    .legend(show=True, title="States", loc="center right") \
    .marker(alpha=0.7) \
    .draw(mvad_pool)
# fmt: on

# %% [markdown]
# ## 5. Working with Simulated State Data
#
# Let's create some simulated state sequences to show other distribution features.
# **Remember**: Only state sequences work with distribution visualization!

# %%
# Generate synthetic STATE sequences for additional examples
synthetic_data = generate_state_sequences(
    n_seq=50,
    seq_size=[20, 25, 30],
    vocabulary=["Active", "Inactive", "Pending", "Completed"],
    missing_data=0.0,
    entity_feature="status",
    seed=42,
)

# Create synthetic STATE sequence pool
synthetic_settings = StateSequenceSettings(
    id_column="id",
    start_column="start_date",
    default_end_value=datetime.now(),
    entity_features=["status"],
)

synthetic_pool = StateSequencePool(synthetic_data, synthetic_settings)
synthetic_pool

# %% [markdown]
# ## 6. Relative Time Distributions
#
# We can align sequences to a common starting point for pattern comparison.

# %%
# Convert synthetic data to relative time
synthetic_pool.to_relative_time(granularity="day")

# Relative time distribution
# fmt: off
SequenceVisualizer.distribution(
    distribution_type="percentage",
    relative_time=True,
    granularity="day"
) \
    .colors("Accent") \
    .title("State Distribution with Relative Time") \
    .legend(show=True, title="Status") \
    .x_axis(label="Days from Start") \
    .draw(synthetic_pool)
# fmt: on

# %% [markdown]
# ## 7. Theming and Customization
#
# TanaT allows changing the visual appearance using themes and custom styling.

# %%
# Dark theme distribution

# This shows the state distribution with a dark background
# fmt: off
SequenceVisualizer.distribution(
    distribution_type="percentage",
    granularity="day"
) \
    .colors("tab20") \
    .title("Dark Theme Distribution") \
    .legend(show=True, title="States") \
    .set_theme("dark_background") \
    .draw(synthetic_pool)
# fmt: on

# %% [markdown]
# ## 8. Working with Individual State Sequences
#
# Distribution visualization can also be applied to single state sequences
# (though it's more meaningful for pools).

# %%
# Single sequence distribution (less common but possible)
single_sequence = synthetic_pool["seq-0"]
# fmt: off
SequenceVisualizer.distribution(granularity="day") \
    .title("Single State Sequence Distribution") \
    .colors("Set2") \
    .legend(show=True) \
    .draw(single_sequence)
# fmt: on

# %% [markdown]
# ## 9. Why Only State Sequences?
#
# Distribution visualizations are specifically designed for state sequences because:
#
# * **States have duration**: They occupy time periods, making "proportion at time t" meaningful
# * **Mutual exclusivity**: An individual can only be in one state at any given time
# * **Continuous coverage**: State sequences typically cover the entire observation period
# * **Meaningful aggregation**: Summing proportions across states gives 100% at each time point
#
# **Event sequences** show discrete occurrences and don't have inherent durations for proportion calculation.
# **Interval sequences** could theoretically work - a work in progress.

# %% [markdown]
# ## 10. Viewing Current Settings
#
# You can inspect the current visualization settings before drawing.

# %%
# Create visualizer and view settings
dist_viz = SequenceVisualizer.distribution()
dist_viz.view_settings()

# %% [markdown]
# ## 11. Saving Visualizations
#
# Visualizations can be saved to disk with custom resolution and file formats.

# %%
# Save with high resolution

# This saves the state distribution analysis as a PNG file
# fmt: off
SequenceVisualizer.distribution(
    distribution_type="percentage",
    granularity="day"
) \
    .colors("Paired") \
    .title("State Distribution Analysis") \
    .legend(show=True, title="States", loc="upper right") \
    .draw(synthetic_pool) \
    .save("state_distribution_analysis.png", dpi=300)
# fmt: on
