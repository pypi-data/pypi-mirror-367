"""
Histogram Visualization
=======================

This module demonstrates how to visualize sequence data using histogram representations.
Histogram visualizations show frequency or duration distributions for sequence elements,
making them ideal for analyzing occurrence patterns, time spent in states, or event frequencies.
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

# Histogram visualization
from tanat.visualization.sequence import SequenceVisualizer

# %% [markdown]
# ## 1. Event Sequence Histograms
#
# We'll start with event sequences to show frequency distributions of discrete events.

# %%
# Generate event sequences for web user behavior
event_data = generate_event_sequences(
    n_seq=100,
    seq_size=[10, 15, 20, 25],
    vocabulary=["PageView", "Click", "Purchase", "Search", "Login", "Logout"],
    missing_data=0.05,
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
print(f"Event pool: {len(event_pool.unique_ids)} user sessions")
event_pool

# %% [markdown]
# ## 2. Basic Frequency Histograms
#
# Frequency histograms show how often each event type occurs across all sequences.

# %%
# Basic occurrence histogram

# Basic histogram showing event counts
# fmt: off
SequenceVisualizer.histogram() \
    .title("User Action Frequency Distribution") \
    .colors("Set2") \
    .legend(show=True, title="Actions", loc="upper right") \
    .x_axis(label="Action Types") \
    .y_axis(label="Frequency") \
    .draw(event_pool)
# fmt: on

# %%
# Single sequence histogram for comparison
single_session = event_pool["seq-0"]
# fmt: off
SequenceVisualizer.histogram() \
    .title("Single User Session - Action Frequency") \
    .colors("tab10") \
    .legend(show=True, loc="upper right") \
    .draw(single_session)
# fmt: on

# %% [markdown]
# ## 3. Different Display Modes
#
# Histograms can show occurrence counts, frequency rates, or time spent.

# %%
# Occurrence count (default mode)

# Histogram showing raw counts of each action
# fmt: off
SequenceVisualizer.histogram(show_as="occurrence") \
    .title("Action Occurrence Counts") \
    .colors("tab10") \
    .legend(show=True, title="User Actions", loc="upper right") \
    .draw(event_pool)
# fmt: on

# %%
# Frequency mode (normalized counts)

# Histogram showing relative frequency of each action
# fmt: off
SequenceVisualizer.histogram(show_as="frequency") \
    .title("Action Frequency Distribution") \
    .colors("Accent") \
    .legend(show=True, title="Actions", loc="upper right") \
    .y_axis(label="Relative Frequency") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 4. Bar Ordering Options
#
# Control the order of bars for better visualization of patterns.

# %%
# Descending order - most frequent first

# Histogram showing actions ordered by frequency
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Most Frequent Actions First") \
    .colors("Dark2") \
    .legend(show=True, loc="upper right") \
    .draw(event_pool)
# fmt: on

# %%
# Ascending order - least frequent first

# Histogram showing actions ordered by frequency, least to most
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence", 
    bar_order="ascending"
) \
    .title("Least Frequent Actions First") \
    .colors("Paired") \
    .legend(show=True, loc="lower right") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 5. Orientation Options
#
# Horizontal bars can be more readable for certain data types.

# %%
# Horizontal histogram - useful for long category names

# Histogram showing actions in horizontal layout
# fmt: off
SequenceVisualizer.histogram(
    show_as="frequency",
    bar_order="descending", 
    orientation="horizontal"
) \
    .title("User Actions - Horizontal View") \
    .colors("Set1") \
    .legend(show=True, title="Actions", loc="upper right") \
    .x_axis(label="Frequency") \
    .y_axis(label="Action Types") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 6. State Sequence Histograms - Time Spent Analysis
#
# For state sequences, we can analyze time spent in different states.

# %%
# Generate state sequences for system monitoring
state_data = generate_state_sequences(
    n_seq=50,
    seq_size=[15, 20, 25],
    vocabulary=["Running", "Idle", "Maintenance", "Error", "Shutdown"],
    missing_data=0.1,
    entity_feature="system_status",
    seed=42,
)

# Create state sequence pool
state_settings = StateSequenceSettings(
    id_column="id",
    start_column="start_date",
    default_end_value=datetime.now(),  # Avoid warning
    entity_features=["system_status"],
)

state_pool = StateSequencePool(state_data, state_settings)
# Set granularity for time calculations
state_pool.to_relative_time(granularity="hour")
print(f"State pool: {len(state_pool.unique_ids)} system monitoring sequences")
state_pool

# %%
# Time spent histogram - shows duration in each state

# Histogram showing total time spent in each state
# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending",
    granularity="hour"
) \
    .title("System Time Spent Analysis (Hours)") \
    .colors("coolwarm") \
    .legend(show=True, title="System Status", loc="upper right") \
    .x_axis(label="System States") \
    .y_axis(label="Total Hours") \
    .draw(state_pool)
# fmt: on

# %%
# Horizontal time spent view for better readability

# Histogram showing time spent in each state, horizontal layout
# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending",
    orientation="horizontal", 
    granularity="hour"
) \
    .title("System Uptime Analysis") \
    .colors("RdYlBu") \
    .legend(show=True, title="Status", loc="upper right") \
    .x_axis(label="Hours") \
    .y_axis(label="System States") \
    .draw(state_pool)
# fmt: on

# %% [markdown]
# ## 7. Interval Sequence Histograms
#
# Interval sequences can show both occurrence and duration distributions.

# %%
# Generate interval sequences for activity tracking
interval_data = generate_interval_sequences(
    n_seq=40,
    seq_size=[8, 12, 16],
    vocabulary=["Meeting", "Email", "Development", "Break", "Planning"],
    missing_data=0.05,
    entity_feature="work_activity",
    seed=42,
)

# Create interval sequence pool
interval_settings = IntervalSequenceSettings(
    id_column="id",
    start_column="start_date",
    end_column="end_date",
    entity_features=["work_activity"],
)

interval_pool = IntervalSequencePool(interval_data, interval_settings)
print(f"Interval pool: {len(interval_pool.unique_ids)} work activity logs")
interval_pool

# %%
# Occurrence histogram for intervals

# Histogram showing count of each work activity
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Work Activity Frequency") \
    .colors("tab20") \
    .legend(show=True, title="Activities", loc="upper right") \
    .x_axis(label="Activity Types") \
    .y_axis(label="Number of Sessions") \
    .draw(interval_pool)
# fmt: on

# %%
# Time spent in different activities

# Histogram showing total time spent in each work activity
# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending",
    orientation="horizontal"
) \
    .title("Time Allocation by Activity") \
    .colors("Spectral") \
    .legend(show=True, title="Work Activities", loc="upper right") \
    .x_axis(label="Total Time") \
    .y_axis(label="Activity Types") \
    .draw(interval_pool)
# fmt: on

# %% [markdown]
# ## 8. Custom Color Mappings
#
# Apply specific colors for meaningful categorical representation.

# %%
# Define custom colors for work activities
activity_colors = {
    "Meeting": "#FF6B6B",  # Red - Meetings
    "Email": "#4ECDC4",  # Teal - Email
    "Development": "#45B7D1",  # Blue - Coding
    "Break": "#96CEB4",  # Green - Breaks
    "Planning": "#FECA57",  # Yellow - Planning
}

# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending"
) \
    .colors(activity_colors) \
    .title("Work Time Distribution - Custom Colors") \
    .legend(show=True, title="Activities", loc="upper right") \
    .x_axis(label="Activities") \
    .y_axis(label="Time Spent") \
    .draw(interval_pool)
# fmt: on

# %% [markdown]
# ## 9. Theming and Advanced Styling
#
# Apply different themes and advanced styling options.

# %%
# Dark theme histogram

# Histogram showing activity distribution with dark theme
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .colors("tab20") \
    .title("Activity Distribution - Dark Theme") \
    .legend(show=True, title="Activities", loc="upper right") \
    .set_theme("dark_background") \
    .draw(interval_pool)
# fmt: on

# %%
# Custom marker styling (for histogram bars)

# Histogram showing styled bars with custom marker settings
# fmt: off
SequenceVisualizer.histogram(
    show_as="frequency",
    bar_order="descending"
) \
    .colors("Set3") \
    .title("Styled Frequency Distribution") \
    .marker(alpha=0.8) \
    .legend(show=True, title="Actions", loc="upper right") \
    .draw(event_pool)
# fmt: on

# %% [markdown]
# ## 10. Settings Inspection and Debugging
#
# View current settings and examine data preparation.

# %%
# Create histogram visualizer and inspect settings
histogram_viz = SequenceVisualizer.histogram()
histogram_viz.view_settings()

# %%
# Examine prepared data structure
prepared_data = histogram_viz.prepare_data(event_pool)
print("Histogram data structure:")
prepared_data.head(10)

# %% [markdown]
# ## 11. Saving Histogram Visualizations
#
# Export histograms with various formats and resolutions.

# %%
# Save high-resolution histogram

# Histogram showing work activity time analysis, saved as PNG
# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending",
    orientation="horizontal"
) \
    .colors("Set1") \
    .title("Work Activity Time Analysis - Final Report") \
    .legend(show=True, title="Activities", loc="upper right") \
    .x_axis(label="Time Spent (Hours)") \
    .y_axis(label="Activity Types") \
    .draw(interval_pool) \
    .save("work_activity_histogram.png", dpi=300)
# fmt: on
