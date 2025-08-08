"""
Timeline Visualization
======================

This module demonstrates how to visualize sequence data using timeline representations.
Timeline visualizations show sequences over time with temporal alignment, making them
ideal for analyzing event patterns, state durations, and temporal relationships.
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
    EventSequenceSettings,
    StateSequenceSettings,
    IntervalSequenceSettings,
)

# Timeline visualization
from tanat.visualization.sequence import SequenceVisualizer

# %% [markdown]
# ## 1. Event Sequence Timelines
#
# We'll start with event sequences to demonstrate basic timeline functionality.
# Event sequences show discrete events occurring at specific points in time.

# %%
# Generate event sequences
event_data = generate_event_sequences(
    n_seq=30,
    seq_size=[15, 20, 25, 30],
    vocabulary=["Login", "Purchase", "Logout", "Support"],
    missing_data=0.0,
    entity_feature="action",
    seed=42,
)

# Create event sequence pool
event_settings = EventSequenceSettings(
    id_column="id",
    time_column="date",
    entity_features=["action"],
)

event_pool = EventSequencePool(event_data, event_settings)
print(f"Event pool: {len(event_pool.unique_ids)} sequences")
event_pool

# %% [markdown]
# ## 2. Basic Timeline Visualization
#
# Timeline visualizations can render individual sequences or entire pools with
# different stacking and temporal alignment options.

# %%
# Basic timeline with default settings

# This shows a timeline by user actions.
# fmt: off
SequenceVisualizer.timeline() \
    .title("User Action Timeline") \
    .legend(show=True, title="Actions", loc="upper right") \
    .draw(event_pool)
# fmt: on

# %%
# Single sequence timeline for detailed view
single_sequence = event_pool["seq-0"]
# fmt: off
SequenceVisualizer.timeline() \
    .title("Single User Journey") \
    .colors("Set2") \
    .marker(size=30, alpha=0.8) \
    .legend(show=True, title="User Actions", loc="upper right") \
    .y_axis(show=True, label="User ID") \
    .draw(single_sequence)
# fmt: on

# %% [markdown]
# ## 3. Stacking Modes
#
# Different stacking modes organize multiple sequences in various ways.

# %%
# Category stacking - groups similar sequences

# Explicitly stacks sequences by their categories (e.g., actions).
# fmt: off
SequenceVisualizer.timeline(stacking_mode="by_category") \
    .title("Timeline by Category Stacking") \
    .colors("tab10") \
    .legend(show=True, loc="center right") \
    .draw(event_pool)
# fmt: on

# %%
# Flat stacking - each sequence on its own row

# This shows each sequence as a separate row, useful for comparing patterns.
# fmt: off
SequenceVisualizer.timeline(stacking_mode="flat") \
    .title("Flat Timeline - One Sequence per Row") \
    .colors("Paired") \
    .marker(spacing=0.8, size=8) \
    .legend(show=True, loc="center right") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 4. Relative Time Alignment
#
# Relative time mode aligns all sequences to a common starting point for pattern comparison.

# %%
# Relative time timeline

# Aligns all sequences to start from the first event in each sequence.
# fmt: off
SequenceVisualizer.timeline(
    relative_time=True,
    granularity="day",
    stacking_mode="flat"
) \
    .title("User Actions - Relative Timeline (Days)") \
    .colors("Accent") \
    .marker(size=10, alpha=0.7, spacing=0.6) \
    .legend(show=True, title="Actions", loc="upper right") \
    .x_axis(label="Days from Start") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 5. State Sequence Timelines
#
# State sequences show periods/durations rather than discrete events.

# %%
# Generate state sequences
state_data = generate_state_sequences(
    n_seq=25,
    seq_size=[10, 15, 20],
    vocabulary=["Active", "Inactive", "Maintenance", "Error"],
    missing_data=0.1,
    entity_feature="status",
    seed=42,
)

# Create state sequence pool
state_settings = StateSequenceSettings(
    id_column="id",
    start_column="start_date",
    entity_features=["status"],
    default_end_value=datetime.now(),
)

state_pool = StateSequencePool(state_data, state_settings)
print(f"State pool: {len(state_pool.unique_ids)} sequences")
state_pool

# %%
# State timeline visualization

# This shows a timeline of system states over time.
# fmt: off
SequenceVisualizer.timeline(stacking_mode="flat") \
    .title("System Status Timeline") \
    .colors("Set1") \
    .marker(spacing=0.9) \
    .legend(show=True, title="System Status", loc="center left") \
    .x_axis(label="Time") \
    .draw(state_pool)
# fmt: on

# %% [markdown]
# ## 6. Interval Sequence Timelines
#
# Interval sequences have both start and end times, showing duration explicitly.

# %%
# Generate interval sequences
interval_data = generate_interval_sequences(
    n_seq=30,
    seq_size=[8, 12, 15],
    vocabulary=["Meeting", "Break", "Work", "Travel"],
    missing_data=0.05,
    entity_feature="activity",
    seed=42,
)

# Create interval sequence pool
interval_settings = IntervalSequenceSettings(
    id_column="id",
    start_column="start_date",
    end_column="end_date",
    entity_features=["activity"],
)

interval_pool = IntervalSequencePool(interval_data, interval_settings)
print(f"Interval pool: {len(interval_pool.unique_ids)} sequences")
interval_pool

# %%
# Interval timeline with temporal alignment
#
# Align all sequences to start from the 7th interval (0-based indexing)
# This sets the 7th interval as the reference point (T=0) for all sequences
interval_pool.zero_from_position(7)  # Set 7th interval as temporal baseline

# fmt: off
SequenceVisualizer.timeline(
    relative_time=True,
    granularity="hour",
    stacking_mode="flat"
) \
    .title("Daily Activity Timeline (Hours)") \
    .colors("Set2") \
    .marker(spacing=0.9, alpha=0.8) \
    .legend(show=True, title="Activities", loc="upper right") \
    .x_axis(label="Hours from Start") \
    .draw(interval_pool)
# fmt: on

# %% [markdown]
# ## 7. Advanced Customization
#
# Timeline visualizations support extensive customization of markers, colors, and themes.

# %%
# Custom color mapping for specific categories
custom_colors = {
    "Login": "#2E8B57",  # Sea Green
    "Purchase": "#FF6347",  # Tomato
    "Logout": "#4682B4",  # Steel Blue
    "Support": "#DAA520",  # Golden Rod
}

# fmt: off
SequenceVisualizer.timeline(relative_time=True) \
    .colors(custom_colors) \
    .title("Custom Colored User Timeline") \
    .marker(
        size=14,
        shape="D",  # Diamond
        edge_color="black",
        alpha=0.9,
        spacing=0.5
    ) \
    .legend(show=True, title="User Actions", loc="upper right") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 8. Theme Applications
#
# Apply different themes for various presentation contexts.

# %%
# Dark theme timeline

# This shows a timeline with a dark background.
# fmt: off
SequenceVisualizer.timeline(
    stacking_mode="flat",
    relative_time=True
) \
    .colors("tab20") \
    .title("Timeline - Dark Theme") \
    .marker(size=10, alpha=0.9) \
    .legend(show=True, title="Actions", loc="upper right") \
    .set_theme("dark_background") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 9. Viewing Settings and Debugging
#
# Inspect current settings for troubleshooting and understanding configurations.

# %%
# View current timeline settings
timeline_viz = SequenceVisualizer.timeline()
timeline_viz.view_settings()

# %%
# Examine the prepared data structure
data_preview = timeline_viz.prepare_data(event_pool)
print("Prepared data sample:")
data_preview.head()

# %% [markdown]
# ## 10. Saving Timeline Visualizations
#
# Export timelines with custom resolution and file formats.

# %%
# High-resolution timeline export

# This saves the timeline visualization to a PNG file with 300 DPI.
# fmt: off
SequenceVisualizer.timeline(
    relative_time=True,
    stacking_mode="flat"
) \
    .title("User Journey Analysis - Final") \
    .colors("Set3") \
    .marker(size=8, alpha=0.8) \
    .legend(show=True, title="User Actions", loc="best") \
    .x_axis(label="Timeline (Days)") \
    .draw(event_pool) \
    .save("user_timeline_analysis.png", dpi=300)
# fmt: on
