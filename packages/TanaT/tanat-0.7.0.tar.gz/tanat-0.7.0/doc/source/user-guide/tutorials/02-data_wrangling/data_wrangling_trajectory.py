# %% [markdown]
# # Data Wrangling for Trajectories
#
# This notebook demonstrates advanced data wrangling techniques for trajectory data in *TanaT*. Trajectories represent the complete patient journey by combining multiple sequence types (events, states, intervals) into unified analytical structures. This multi-dimensional approach enables sophisticated filtering and analysis across different temporal data modalities.
#
# These techniques are essential for:
# - Preparing complex multi-modal datasets for machine learning models
# - Extracting patient cohorts based on cross-sequence patterns
# - Analyzing care pathways and treatment trajectories
# - Creating comprehensive analysis-ready healthcare datasets

# %% [markdown]
# ### Required imports

# %%
from datetime import datetime
import pandas as pd
import numpy as np

# Simulation imports
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
    generate_interval_sequences,
    generate_state_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
    StateSequencePool,
    IntervalSequencePool,
)

# Trajectory pool
from tanat.trajectory import TrajectoryPool

# Criterion for filtering
from tanat.criterion import (
    QueryCriterion,
    PatternCriterion,
    StaticCriterion,
)

# Visualization
from tanat.visualization.sequence import SequenceVisualizer

# %% [markdown]
# ## 1. Trajectory Data Setup <a class="anchor" id="1-data-setup"></a>
#
# Trajectories integrate multiple sequence types to represent complete patient journeys. We'll create a comprehensive healthcare dataset with events (visits), states (health conditions), and intervals (medication periods) that reflect real-world clinical complexity.

# %% [markdown]
# ### Dataset Configuration
#
# Define parameters for our multi-modal healthcare trajectory dataset.

# %%
# Dataset parameters
N_SEQ = 150  # Number of patient trajectories
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42  # For reproducible results

# %% [markdown]
# ### Medical Visit Events
#
# Generate healthcare visit sequences representing diverse clinical encounters and care coordination.

# %%
# Comprehensive healthcare visit types including surgical procedures
visit_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "GENERAL_PRACTITIONER",
        "SPECIALIST",
        "EMERGENCY",
        "LABORATORY",
        "RADIOLOGIST",
        "SURGERY",
        "PHARMACY",
    ],
    missing_data=0.12,
    entity_feature="visit_type",
    seed=SEED,
)

visit_data.describe(include="all")  # Display summary statistics

# %% [markdown]
# ### Health State Sequences
#
# Generate health condition sequences with expanded vocabulary including disease progression and recovery patterns.

# %%
# Extended health states covering full disease trajectory
health_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "HEALTHY",
        "ACUTE_ILLNESS",
        "TREATMENT",
        "RECOVERY",
        "CHRONIC_MONITORING",
        "REMISSION",
        "DETERIORATION",
    ],
    missing_data=0.08,  # Lower missing rate for health states
    entity_feature="health_state",
    seed=SEED,
)

health_data.describe(include="all")  # Display summary statistics

# %% [markdown]
# ### Medication Interval Sequences
#
# Generate medication prescription periods including high-intensity treatments for complex conditions.

# %%
# Comprehensive medication categories including intensive treatments
medication_data = generate_interval_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=[
        "ANTIBIOTIC",
        "PAIN_RELIEVER",
        "CORTICOSTEROID",
        "ANTICOAGULANT",
        "ANTIHYPERTENSIVE",
        "INSULIN",
        "CHEMOTHERAPY",
    ],
    missing_data=0.15,
    entity_feature="medication",
    seed=SEED,
)

medication_data.describe(include="all")  # Display summary statistics

# %% [markdown]
# ### Data Generation Summary
#
# Overview of the multi-modal trajectory components we'll integrate.

# %%
print("Trajectory dataset components:")
print(f"- Medical visits: {len(visit_data)} records")
print(f"- Health states: {len(health_data)} records")
print(f"- Medication periods: {len(medication_data)} records")
print(f"- Total patients: {N_SEQ}")

# %% [markdown]
# ### Comprehensive Patient Demographics
#
# Generate rich patient profiles with demographics, clinical characteristics, and risk factors that reflect real-world healthcare complexity.


# %%
def generate_comprehensive_patient_data(n_patients, seed=42):
    """
    Generate comprehensive patient demographic and clinical data with age-dependent risk factors.

    Parameters:
    - n_patients: Number of patient records to generate
    - seed: Random seed for reproducibility

    Returns:
    - DataFrame with comprehensive patient characteristics
    """
    np.random.seed(seed)

    patients = []
    for i in range(n_patients):
        patient_id = f"seq-{i}"
        age = np.random.randint(18, 90)

        # Age-dependent chronic condition probability (realistic healthcare patterns)
        chronic_prob = 0.2 if age < 40 else 0.4 if age < 65 else 0.7

        patients.append(
            {
                "id": patient_id,
                "age": age,
                "age_group": "18-40" if age < 40 else "40-65" if age < 65 else "65+",
                "gender": np.random.choice(["M", "F"], p=[0.48, 0.52]),
                "insurance_type": np.random.choice(
                    ["PUBLIC", "PRIVATE", "MIXED"], p=[0.6, 0.25, 0.15]
                ),
                "chronic_condition": np.random.choice(
                    [True, False], p=[chronic_prob, 1 - chronic_prob]
                ),
                "risk_level": np.random.choice(
                    ["LOW", "MEDIUM", "HIGH"], p=[0.5, 0.3, 0.2]
                ),
                "comorbidity_count": np.random.poisson(1.5),
                "bmi_category": np.random.choice(
                    ["NORMAL", "OVERWEIGHT", "OBESE"], p=[0.4, 0.35, 0.25]
                ),
                "smoking_status": np.random.choice(
                    ["NEVER", "FORMER", "CURRENT"], p=[0.6, 0.25, 0.15]
                ),
                "family_history": np.random.choice([True, False], p=[0.3, 0.7]),
            }
        )

    return pd.DataFrame(patients)


# %% [markdown]
# ### Generate and Examine Patient Data
#
# Create comprehensive patient demographics with realistic healthcare risk factor distributions.

# %%
# Generate comprehensive patient demographics
static_data = generate_comprehensive_patient_data(N_SEQ, seed=SEED)

# %%
# Examine demographic and clinical distributions
static_data.describe(include="all")

# %% [markdown]
# ### Trajectory Pool Architecture
#
# Trajectory pools integrate multiple sequence types into unified analytical structures. Each sequence type maintains its specific temporal properties while enabling cross-sequence filtering and analysis.

# %% [markdown]
# ### Define Shared Static Features
#
# Establish the comprehensive set of patient characteristics that will be available across all sequence types.

# %%
# Comprehensive static feature set for trajectory analysis
static_features = [
    "age",
    "age_group",
    "gender",
    "insurance_type",
    "chronic_condition",
    "risk_level",
    "comorbidity_count",
    "bmi_category",
    "smoking_status",
    "family_history",
]

print(f"Static features for trajectory integration: {len(static_features)} variables")
print("Features:", static_features)

# %% [markdown]
# ### Medical Visit Sequence Pool Setup
#
# Configure the event pool to handle healthcare visit sequences with comprehensive patient demographics.

# %%
# Create medical visit sequence pool
visit_pool = EventSequencePool(
    visit_data,
    {
        "id_column": "id",
        "time_column": "date",
        "entity_features": ["visit_type"],
        "static_features": static_features,
    },
    static_data=static_data,
)

# Report pool creation
visit_pool

# %% [markdown]
# ### Health State Sequence Pool Setup
#
# Configure the state pool to handle health condition sequences with temporal persistence.

# %%
# Create health state sequence pool
health_pool = StateSequencePool(
    health_data,
    {
        "id_column": "id",
        "start_column": "start_date",
        "default_end_value": datetime.now(),  # Avoid warnings for open-ended states
        "entity_features": ["health_state"],
        "static_features": static_features,
    },
    static_data=static_data,
)

# Report pool creation
health_pool

# %% [markdown]
# ### Medication Sequence Pool Setup
#
# Configure the interval pool to handle medication periods with defined durations.

# %%
# Create medication interval sequence pool
medication_pool = IntervalSequencePool(
    medication_data,
    {
        "id_column": "id",
        "start_column": "start_date",
        "end_column": "end_date",
        "entity_features": ["medication"],
        "static_features": static_features,
    },
    static_data=static_data,
)

# Report pool creation
medication_pool

# %% [markdown]
# ### Trajectory Pool Integration
#
# Combine all sequence pools into a unified trajectory structure for comprehensive multi-modal analysis.

# %%
# Initialize empty trajectory pool and add sequence pools
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(visit_pool, "medical_visits")
trajectory_pool.add_sequence_pool(health_pool, "health_states")
trajectory_pool.add_sequence_pool(medication_pool, "medications")

# Report sequence pool integration
trajectory_pool

# %%
# Add comprehensive static features to trajectory pool
trajectory_pool.add_static_features(
    static_data, id_column="id", static_features=static_features
)

# %%
# Configure trajectory pool settings
trajectory_pool.update_settings(
    # Use union of IDs across sequence pools
    intersection=False,
)


# %%
# Display final trajectory pool summary
trajectory_pool

# %% [markdown]
# ### Multi-Modal Data Distribution
#
# Examine the distribution across all sequence types in our trajectory dataset before applying filtering operations.

# %%
# Visualize visit type distribution across all trajectories
color_map_visit = {
    "GENERAL_PRACTITIONER": "#1f77b4",
    "SPECIALIST": "#ff7f0e",
    "SURGERY": "#2ca02c",
    "RADIOLOGIST": "#d62728",
    "LABORATORY": "#9467bd",
    "EMERGENCY": "#e377c2",
    "PHARMACY": "#7f7f7f",
}
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Medical Visit Distribution - Complete Trajectory Dataset") \
    .colors(color_map_visit) \
    .legend(show=True, title="Visit Types", loc="upper right") \
    .x_axis(label="Visit Types") \
    .y_axis(label="Frequency") \
    .draw(visit_pool)
# fmt: on

# %%
# Visualize medication duration patterns
color_map_medication = {
    "ANTIBIOTIC": "#FF6B6B",
    "PAIN_RELIEVER": "#4ECDC4",
    "CORTICOSTEROID": "#45B7D1",
    "ANTICOAGULANT": "#96CEB4",
    "ANTIHYPERTENSIVE": "#FFEAA7",
    "INSULIN": "#DDA0DD",
    "CHEMOTHERAPY": "#FF8C94",
}
# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending",
    orientation="horizontal"
) \
    .title("Medication Duration Patterns - All Trajectories") \
    .colors(color_map_medication) \
    .legend(show=True, title="Medications", loc="lower right") \
    .x_axis(label="Total Duration") \
    .y_axis(label="Medication Types") \
    .draw(medication_pool)
# fmt: on

# %% [markdown]
# ## 2. Static Data Operations
#
# Static criterion enable filtering entire trajectories based on patient demographics and clinical characteristics. This is essential for creating targeted patient cohorts and population-based analyses.

# %% [markdown]
# ### Single Criterion Trajectory Filtering
#
# Filter trajectories based on individual patient characteristics to create focused analytical cohorts.

# %%
# Filter for high-risk patients across all trajectory components
high_risk_criterion = StaticCriterion(query="risk_level == 'HIGH'")
high_risk_trajectories = trajectory_pool.filter(high_risk_criterion, level="trajectory")

# Report high-risk cohort selection
high_risk_trajectories

# %% [markdown]
# ### Multi-Criteria Trajectory Filtering
#
# Combine multiple patient characteristics for sophisticated cohort selection and population targeting.

# %%
# Define complex clinical cohort: elderly patients with multiple risk factors
complex_criterion = StaticCriterion(
    query="age >= 65 and chronic_condition == True and comorbidity_count >= 2"
)
complex_cohort = trajectory_pool.filter(complex_criterion, level="trajectory")

# Report complex cohort selection
complex_cohort

# %%
# Compare cohort selection strategies
elderly_only = trajectory_pool.filter(
    StaticCriterion(query="age >= 65"), level="trajectory"
)
chronic_only = trajectory_pool.filter(
    StaticCriterion(query="chronic_condition == True"), level="trajectory"
)

print("Cohort selection comparison:")
print(f"- Elderly only (≥65): {len(elderly_only)} trajectories")
print(f"- Chronic condition only: {len(chronic_only)} trajectories")
print(f"- Complex multi-criteria: {len(complex_cohort)} trajectories")

# %% [markdown]
# %% [markdown]
# ## 3. Sequence-Specific Filtering <a class="anchor" id="3-sequence-filtering"></a>
#
# Trajectory filtering can target specific sequence types within the multi-modal structure. This enables precise selection based on patterns in medical visits, health states, or medication usage while maintaining the complete trajectory context.

# %% [markdown]
# ### Medical Visit Pattern Filtering
#
# Identify trajectories based on specific healthcare utilization patterns and care pathways.

# %%
# Examine the medical visit sequence pool structure
print("Medical visit sequence pool overview:")
print(f"Total patients: {len(trajectory_pool.sequence_pools['medical_visits'])}")
print(f"Visit types: {trajectory_pool.sequence_pools['medical_visits'].vocabulary}")

# %%
# Filter trajectories containing emergency visits
emergency_criterion = QueryCriterion(query="visit_type == 'EMERGENCY'")
emergency_trajectories = trajectory_pool.filter(
    emergency_criterion,
    level="sequence",
    sequence_name="medical_visits",
    # Propagate filtering to trajectory level
    intersection=True,
)

# Report emergency visit analysis
emergency_trajectories

# %%
# Filter trajectories containing surgical procedures
surgery_criterion = QueryCriterion(query="visit_type == 'SURGERY'")
surgery_trajectories = trajectory_pool.filter(
    surgery_criterion,
    level="sequence",
    sequence_name="medical_visits",
    intersection=True,  # Propagate filtering to trajectory level
)

# Report surgery visit analysis
surgery_trajectories

# %%
# Analyze care pathway complexity: trajectories with both emergency and surgery
emergency_ids = emergency_trajectories.unique_ids
surgery_ids = surgery_trajectories.unique_ids
complex_care_ids = emergency_ids.intersection(surgery_ids)

print("Complex care pathway analysis:")
print(f"Emergency only: {len(emergency_ids - surgery_ids)} trajectories")
print(f"Surgery only: {len(surgery_ids - emergency_ids)} trajectories")
print(f"Both emergency and surgery: {len(complex_care_ids)} trajectories")
print(f"Complex care rate: {len(complex_care_ids)/len(trajectory_pool)*100:.1f}%")

# %%
# Visualize visit patterns in complex care trajectories
complex_care_trajectories = trajectory_pool.subset(complex_care_ids)
# fmt: off
SequenceVisualizer.histogram(
    show_as="occurrence",
    bar_order="descending"
) \
    .title("Visit Patterns in Complex Care Trajectories (Emergency + Surgery)") \
    .colors(color_map_visit) \
    .legend(show=True, title="Visit Types", loc="upper right") \
    .x_axis(label="Visit Types") \
    .y_axis(label="Frequency") \
    .draw(complex_care_trajectories.sequence_pools["medical_visits"])
# fmt: on

# %% [markdown]
# ### Health State Pattern Analysis
#
# Identify trajectories based on disease progression patterns and health state transitions.

# %%
# Filter trajectories containing treatment states
treatment_criterion = PatternCriterion(
    pattern={"health_state": "TREATMENT"}, contains=True
)
treatment_trajectories = trajectory_pool.filter(
    treatment_criterion,
    level="sequence",
    sequence_name="health_states",
    # Propagate filtering to trajectory level
    intersection=True,
)


# Report treatment state analysis
treatment_trajectories

# %%
# Filter trajectories with illness-to-treatment progression pattern
progression_criterion = PatternCriterion(
    pattern={"health_state": ["ACUTE_ILLNESS", "TREATMENT"]},
    contains=True,  # Sequential pattern must exist somewhere in sequence
)
progression_trajectories = trajectory_pool.filter(
    progression_criterion,
    level="sequence",
    sequence_name="health_states",
    intersection=True,  # Propagate filtering to trajectory level
)

# Report illness-to-treatment progression analysis
progression_trajectories

# %%
# Visualize health progression patterns with timeline
# fmt: off
SequenceVisualizer.timeline(
    stacking_mode="flat",
    relative_time=True,
    granularity="day"
) \
    .title("Health Progression Patterns (Illness → Treatment)") \
    .colors("RdYlBu") \
    .marker(spacing=0.8, alpha=0.7) \
    .legend(show=True, title="Health States", loc="upper right") \
    .x_axis(label="Days from Start") \
    .draw(progression_trajectories.sequence_pools["health_states"])
# fmt: on

# %% [markdown]
# ### Medication Pattern Filtering
#
# Identify trajectories based on medication usage patterns and treatment intensity.

# %%
# Define high-intensity medication categories
intensive_medications = ["CHEMOTHERAPY", "CORTICOSTEROID", "INSULIN"]
intensive_criterion = QueryCriterion(query=f"medication in {intensive_medications}")

intensive_trajectories = trajectory_pool.filter(
    intensive_criterion,
    level="sequence",
    sequence_name="medications",
    intersection=True,  # Propagate filtering to trajectory level
)

# Report intensive medication analysis
intensive_trajectories

# %%
# Analyze medication duration patterns in intensive care trajectories
# fmt: off
SequenceVisualizer.histogram(
    show_as="time_spent",
    bar_order="descending",
    orientation="horizontal"
) \
    .title("Medication Duration in Intensive Care Trajectories") \
    .colors(color_map_medication) \
    .legend(show=True, title="Medications", loc="lower right") \
    .x_axis(label="Total Duration") \
    .y_axis(label="Medication Types") \
    .draw(intensive_trajectories.sequence_pools["medications"])
# fmt: on

# %% [markdown]
# ## 4. Reference Date Management
#
# Trajectory-level reference dating enables temporal alignment across multiple sequence types. This is essential for analyzing care coordination, treatment timing, and cross-sequence temporal relationships.

# %% [markdown]
# ### Default Temporal Alignment
#
# By default, trajectories use the earliest timestamp across all sequence types as the reference point.

# %%
# Create copy for temporal alignment demonstration
aligned_trajectory_pool = trajectory_pool.copy()

# Apply default reference dating (first entity across all sequences)
aligned_trajectory_pool.zero_from_position(0)  # Mimic default behavior

# Display T zero reference point
pd.DataFrame.from_dict(
    aligned_trajectory_pool.t_zero,
    orient="index",
    columns=["T0 Date"],
)


# %%
# Transform medical visits to relative time from default T0
# fmt: off
aligned_trajectory_pool.sequence_pools["medical_visits"] \
                    .to_relative_time(
                        granularity="day",
                        drop_na=True,
                    )
# fmt: on

# %% [markdown]
# ### Event-Based Reference Dating
#
# Set common reference dates based on specific clinical events for targeted temporal analysis.

# %%
# Create new copy for event-based alignment
event_aligned_pool = trajectory_pool.copy()

# Set T0 based on first emergency visit across trajectories
event_aligned_pool.zero_from_query(
    query="visit_type == 'EMERGENCY'",  # T0 = first emergency visit
    sequence_name="medical_visits",
    use_first=True,
)

# Report T zero reference point
pd.DataFrame.from_dict(
    event_aligned_pool.t_zero,
    orient="index",
    columns=["T0 Date"],
)

# %%
# Transform medication data relative to emergency visit T0
# fmt: off
event_aligned_pool.sequence_pools["medications"] \
                .to_relative_time(
                    granularity="day",
                    drop_na=True,
                )
# fmt: on


# %% [markdown]
# ## 5. Advanced Trajectory Filtering
#
# Advanced filtering combines multiple criterion and sequence types to create sophisticated patient cohorts. This multi-dimensional approach enables precise population targeting and complex analytical workflows.

# %% [markdown]
# ### Multi-Dimensional Cohort Selection
#
# Build complex patient cohorts by combining demographics, healthcare utilization, and clinical complexity dimensions.

# %%
# Dimension 1: Demographics - elderly patients with risk factors
demo_criterion = StaticCriterion(
    query="age >= 60 and (chronic_condition == True or comorbidity_count >= 2)"
)
demo_cohort = trajectory_pool.filter(demo_criterion, level="trajectory")

# Report demographic cohort selection
demo_cohort

# %%
# Dimension 2: Healthcare utilization - multiple high-acuity visit types
utilization_criterion = QueryCriterion(
    query="visit_type in ['EMERGENCY', 'SPECIALIST', 'SURGERY']"
)
utilization_cohort = demo_cohort.filter(
    utilization_criterion,
    level="sequence",
    sequence_name="medical_visits",
    intersection=True,
)

# Report utilization cohort selection
utilization_cohort

# %%
# Dimension 3: Clinical complexity - illness-to-treatment progression
complexity_criterion = PatternCriterion(
    pattern={"health_state": ["ACUTE_ILLNESS", "TREATMENT"]}, contains=True
)
final_complex_cohort = utilization_cohort.filter(
    complexity_criterion,
    level="sequence",
    sequence_name="health_states",
    intersection=True,
)

# Report final complex cohort selection
final_complex_cohort

# %% [markdown]
# ### Set-Based Trajectory Operations
#
# Use set operations to combine trajectory IDs from different filtering criterion for flexible cohort construction.

# %%
# Step 1: Identify high-risk patients
high_risk_criterion = StaticCriterion(query="risk_level == 'HIGH'")
high_risk_ids = trajectory_pool.which(high_risk_criterion)

print("Set-based trajectory operations:")
print(f"High-risk trajectories: {len(high_risk_ids)}")

# %%
# Step 2: Identify emergency care utilizers
emergency_criterion = QueryCriterion(query="visit_type == 'EMERGENCY'")
emergency_ids = trajectory_pool.sequence_pools["medical_visits"].which(
    emergency_criterion
)

print(f"Emergency care trajectories: {len(emergency_ids)}")

# %%
# Step 3: Identify treatment recipients
treatment_criterion = PatternCriterion(
    pattern={"health_state": "TREATMENT"}, contains=True
)
treatment_ids = trajectory_pool.sequence_pools["health_states"].which(
    treatment_criterion
)

print(f"Treatment trajectories: {len(treatment_ids)}")

# %% [markdown]
# ### Set Operations for Cohort Construction
#
# Combine trajectory sets using union, intersection, and difference operations.

# %%
# Union: High-risk OR emergency care
union_ids = high_risk_ids.union(emergency_ids)
print("Set operation results:")
print(f"Union (high-risk OR emergency): {len(union_ids)} trajectories")

# %%
# Intersection: High-risk AND emergency care
intersection_ids = high_risk_ids.intersection(emergency_ids)
print(f"Intersection (high-risk AND emergency): {len(intersection_ids)} trajectories")

# %%
# Difference: High-risk but NOT emergency care
difference_ids = high_risk_ids - emergency_ids
print(f"Difference (high-risk NOT emergency): {len(difference_ids)} trajectories")

# %%
# Triple intersection: High-risk AND emergency AND treatment
triple_intersection = high_risk_ids.intersection(emergency_ids).intersection(
    treatment_ids
)

# %%
# Create final trajectory subset from triple intersection
comprehensive_cohort = trajectory_pool.subset(triple_intersection)

# Report comprehensive cohort selection
comprehensive_cohort

# %%
# Visualize comprehensive cohort characteristics across all sequence types
# fmt: off
SequenceVisualizer.timeline(
    stacking_mode="by_category",
    relative_time=True,
    granularity="day"
) \
    .title("Comprehensive Cohort: High-Risk + Emergency + Treatment Trajectories") \
    .colors(color_map_visit) \
    .marker(spacing=0.6, alpha=0.8) \
    .legend(show=True, title="Visit Types", loc="upper right") \
    .x_axis(label="Days from Start") \
    .draw(comprehensive_cohort.sequence_pools["medical_visits"])
# fmt: on
