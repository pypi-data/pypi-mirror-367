# %% [markdown]
# # Illustration of TanaT on the MIMIC-IV dataset
#
# ## Overview
#
# This tutorial demonstrates the comprehensive analysis of patient care trajectories using TanaT (Temporal Analysis and Temporal Trajectories) with the MIMIC-IV database. MIMIC-IV is a freely accessible critical care database containing de-identified health records from patients admitted to the Beth Israel Deaconess Medical Center.
#
# **Learning Objectives:**
# - Load and preprocess temporal healthcare data using TanaT
# - Create and visualize patient trajectory sequences
# - Apply trajectory-based clustering to identify patient care patterns
# - Perform survival analysis comparing different patient trajectory clusters
#
# **Dataset Information:**
# The MIMIC-IV database contains comprehensive electronic health records including:
# - Patient demographics and mortality information
# - Hospital admissions with admission types and locations
# - Medical procedures coded with ICD standards
# - Pharmacy prescriptions and medication data
#
# **Data Access:**
# - **Recommended**: TanaT provides direct database access via the `access("mimic4")` function
# - **Alternative**: Manual setup from [PhysioNet MIMIC-IV Demo](https://physionet.org/content/mimic-iv-demo/2.2/) following [MIT-LCP setup procedures](https://github.com/MIT-LCP/mimic-code)
#
# ## Methodology
#
# This analysis follows a systematic approach to longitudinal healthcare data analysis:
#
# 1. **Data Preparation**: Extract and preprocess multi-modal temporal data
# 2. **Trajectory Construction**: Build patient sequences combining events and intervals
# 3. **Exploratory Visualization**: Examine event distributions and individual patient timelines
# 4. **Trajectory Clustering**: Group patients with similar care patterns using temporal metrics
# 5. **Survival Analysis**: Compare clinical outcomes across identified patient clusters
#
# The analysis focuses on admission sequences as the primary trajectory component, examining how different hospitalization patterns relate to patient outcomes.

# %% [markdown]
# ## 1. Data Access and Initial Setup
#
# ### Import Required Libraries and Access MIMIC-IV Database
#
# We begin by importing the necessary libraries and establishing connection to the MIMIC-IV database. TanaT provides convenient direct access to a copy of the MIMIC-IV demo dataset, eliminating the need for manual database setup.

# %%
import pandas as pd
from tanat.dataset import access

# Access MIMIC-IV database through TanaT's built-in interface
# This automatically downloads and provides access to the MIMIC-IV demo dataset
con = access("mimic4")

# %% [markdown]
# ### Data Extraction and Preprocessing
#
# We extract four key data types from MIMIC-IV that will form the basis of our temporal analysis:
#
# 1. **Admissions**: Hospital stays with start/end times, admission types, and locations
# 2. **Patients**: Demographics including age, gender, and mortality dates
# 3. **Procedures**: Medical procedures with timestamps and ICD codes
# 4. **Pharmacy**: Medication prescriptions with administration times
#
# Each query structures the data with consistent temporal columns (`time`, `endtime`) and relevant clinical features for trajectory analysis.

# %%
# Extract hospital admissions with temporal intervals
admissions = pd.read_sql_query(
    'SELECT subject_id, admittime as time, dischtime as endtime, admission_type, admission_location FROM "hosp/admissions"',
    con,
)

# Extract patient demographics and mortality data
patients = pd.read_sql_query(
    'SELECT subject_id, gender, anchor_age as age, dod FROM "hosp/patients"', con
)

# Extract medical procedures with ICD codes
procedures = pd.read_sql_query(
    'SELECT subject_id, chartdate as time, icd_code, icd_version FROM "hosp/procedures_icd"',
    con,
)

# Extract pharmacy/medication data
drugs = pd.read_sql_query(
    'SELECT subject_id, starttime as time, pharmacy_id FROM "hosp/pharmacy"', con
)

# Close database connection
con.close()

# %% [markdown]
# ### Create Death Events from Patient Data
#
# Patient mortality information in MIMIC-IV is stored as static dates in patient records. For trajectory analysis, we transform these dates into temporal events by creating synthetic "admission" records with type 'DEATH'. This approach allows mortality to be integrated naturally into the temporal sequence analysis.

# %%
# Extract death dates and create temporal death events
death_events = patients[patients.dod != ""][["subject_id", "dod"]].rename(
    columns={"dod": "time"}
)
death_events["endtime"] = death_events["time"]  # Point event (start = end time)
death_events["admission_type"] = "DEATH"
death_events["admission_location"] = None  # No location for death events

# Integrate death events into admissions timeline
admissions = pd.concat((admissions, death_events))

# Clean patient data by removing death dates (now in temporal sequences)
patients = patients[["subject_id", "gender", "age"]]

# %% [markdown]
# ### Date Format Conversion
#
# Convert string-formatted timestamps to pandas datetime objects for proper temporal ordering and analysis. This standardization ensures accurate chronological sequence processing across all data types.

# %%
# Convert timestamp strings to datetime objects for temporal analysis
admissions.time = pd.to_datetime(admissions.time.str[:10])
admissions.endtime = pd.to_datetime(admissions.endtime.str[:10])
procedures.time = pd.to_datetime(procedures.time.str[:10])

# %% [markdown]
# ### Sample Data Inspection
#
# Let's examine the structure and content of our preprocessed datasets to verify data quality and understand the characteristics of our patient population.

# %%
# Display sample admission data including created death events
print("Admission data structure (including death events):")
admissions.head()

# %%
# Display patient demographic data
print("Patient demographic structure:")
patients.head()

# %% [markdown]
# ## 2. TanaT Trajectory Construction
#
# ### Import TanaT Modules for Sequence and Trajectory Analysis
#
# Now we transition from raw data to TanaT's trajectory representation. We'll construct two types of sequence pools to capture different aspects of patient care.

# %%
# Import TanaT sequence components
from tanat.sequence import (
    EventSequencePool,
    EventSequenceSettings,
    IntervalSequencePool,
    IntervalSequenceSettings,
)

# Import TanaT trajectory components
from tanat.trajectory import TrajectoryPool, TrajectoryPoolSettings

# %% [markdown]
# ### Create TanaT Sequence Pools
#
# We create two distinct sequence pools representing different temporal aspects of patient care:
#
# 1. **Event Sequences** (Procedures): Point-in-time events with procedure codes
# 2. **Interval Sequences** (Admissions): Duration-based events with admission types and locations
#
# Each sequence pool captures a different dimension of the patient care trajectory, enabling comprehensive temporal analysis.

# %%
# Create procedure event sequence pool
# Procedures are point-in-time events characterized by ICD codes
settings = EventSequenceSettings(
    id_column="subject_id", time_column="time", entity_features=["icd_code"]
)
procedures_pool = EventSequencePool(
    sequence_data=procedures,
    settings=settings,
)
procedures_pool

# %%
# Create admission interval sequence pool
# Admissions have duration and are characterized by type and location
settings = IntervalSequenceSettings(
    id_column="subject_id",
    start_column="time",
    end_column="endtime",
    entity_features=["admission_type", "admission_location"],
)
admissions_pool = IntervalSequencePool(
    sequence_data=admissions,
    settings=settings,
)
admissions_pool

# %% [markdown]
# ### Build Trajectory Pool with Static Features
#
# We combine our sequence pools with static patient data to create comprehensive patient trajectories. This integrated representation enables analysis that considers both temporal patterns and patient characteristics.

# %%
# Configure trajectory pool settings
settings = TrajectoryPoolSettings(
    intersection=False,  # Include patients even if missing some sequence types
    id_column="subject_id",  # Patient identifier for static data linkage
    static_features=["gender", "age"],  # Patient demographic characteristics
)

# Create comprehensive trajectory pool combining sequences and static features
trajpool = TrajectoryPool(
    sequence_pools={"adm": admissions_pool, "proc": procedures_pool},
    static_data=patients,
    settings=settings,
)

# trajectory pool summary
trajpool

# %% [markdown]
# ### Define Index Date (T0) for Trajectories
#
# For relative temporal analysis, we establish a reference time point (T0) for each patient. Rather than using absolute timestamps, we define the index date as the time of the first procedure event, enabling comparison of relative temporal patterns across patients.

# %%
# Define index date using first procedure event for each patient
trajpool.zero_from_query(
    query="icd_code in icd_code",  # Query matching any procedure
    sequence_name="proc",  # Use procedure sequence pool
    use_first=True,  # Take first matching event
    anchor="start",  # Use event start time as reference
)

# Display computed index dates (TO)
pd.DataFrame.from_dict(
    trajpool.t_zero,
    orient="index",
    columns=["T0 Date"],
)

# %% [markdown]
# ### Demonstrate Data Filtering Using Query Criteria
#
# TanaT provides flexible filtering capabilities using query-based criteria. We'll demonstrate filtering to identify patients who experienced mortality during the study period.

# %%
# Import query filtering functionality
from tanat.criterion import QueryCriterion

# Filter for patients with death events at sequence level
death_patients = admissions_pool.filter(
    QueryCriterion(query="admission_type == 'DEATH'"), level="sequence"
)
# Demonstrate same filtering from trajectory pool level
death_patients_traj = trajpool.filter(
    QueryCriterion(query="admission_type == 'DEATH'"),
    level="sequence",
    sequence_name="adm",
)
death_patients_traj

# %% [markdown]
# ## 3. Exploratory Data Visualization
#
# ### Import Visualization Tools
#
# We'll use TanaT's built-in visualization capabilities to explore event distributions and patient timelines before proceeding to advanced analytics.

# %%
# Import TanaT visualization components
from tanat.visualization.sequence import SequenceVisualizer

# %% [markdown]
# ### Visualize Event Distributions
#
# Understanding the frequency and diversity of events in our dataset provides insights into the clinical complexity and helps inform subsequent analysis decisions.

# %%
# Visualize procedure event frequency distribution
# fmt: off
SequenceVisualizer.histogram(bar_order="descending") \
    .title("Procedure Event Distribution") \
    .draw(procedures_pool)
# fmt: on

# %% [markdown]
# The procedure histogram reveals the diversity of medical interventions in the MIMIC-IV dataset. The distribution shows numerous low-frequency procedures, indicating the heterogeneous nature of critical care interventions.

# %%
# Visualize admission events (combining admission type and location)
# fmt: off
SequenceVisualizer.histogram(bar_order="descending") \
    .title("Admission Event Distribution (Type + Location)") \
    .draw(admissions_pool)
# fmt: on

# %%
# Focus on admission type only for clearer clinical interpretation
# fmt: off
SequenceVisualizer.histogram(bar_order="descending") \
    .title("Admission Type Distribution") \
    .draw(admissions_pool, entity_features=["admission_type"])
# fmt: on

# %% [markdown]
# ### Create Timeline Visualizations for Individual Patients
#
# Individual patient timelines provide insights into care trajectory patterns and help validate our data preprocessing. We'll examine a specific patient's admission sequence to understand the temporal structure.

# %%
# Select a representative patient for timeline visualization
ids = admissions_pool.unique_ids
target_id = "10021487"  # Pre-selected patient with interesting trajectory

# Extract individual patient sequence
patient_sequence = admissions_pool[target_id]

# Create timeline visualization for the selected patient
# fmt: off
SequenceVisualizer.timeline() \
    .title(f"Care Timeline for Patient {target_id}") \
    .draw(patient_sequence, entity_features=["admission_type"])
# fmt: on

# %% [markdown]
# ## 4. Trajectory-Based Patient Clustering
#
# ### Clustering Methodology
#
# Traditional patient clustering relies on static demographic or clinical features. TanaT enables clustering based on temporal care patterns, potentially revealing clinically meaningful patient subgroups defined by their healthcare utilization trajectories.
#
# **Clustering Components:**
# 1. **Entity Metric**: How to compare individual admission events (Hamming distance)
# 2. **Sequence Metric**: How to compare entire admission sequences (Linear pairwise alignment)
# 3. **Clustering Algorithm**: Method for grouping similar trajectories (Hierarchical clustering)
#
# **Clinical Rationale:**
# By clustering patients based on admission patterns, we may identify distinct care pathways that correlate with clinical outcomes, resource utilization, or underlying disease processes.

# %% [markdown]
# ### Define Entity and Sequence Metrics for Clustering
#
# We configure metrics that quantify similarity between admission sequences. The hierarchical approach first defines how to compare individual events, then extends this to compare entire sequences.

# %%
# Import clustering metric components
from tanat.metric.entity import HammingEntityMetric, HammingEntityMetricSettings
from tanat.metric.sequence import (
    LinearPairwiseSequenceMetric,
    LinearPairwiseSequenceMetricSettings,
)

# Configure entity-level metric (Hamming distance for categorical features)
hamming_metric = HammingEntityMetric(
    settings=HammingEntityMetricSettings(
        default_value=0.0
    )  # Padding value for sequences of different lengths
)

# Configure sequence-level metric (Linear pairwise alignment)
sequence_metric_settings = LinearPairwiseSequenceMetricSettings(
    entity_metric=hamming_metric,  # Use Hamming distance for individual event comparison
)
linear_metric = LinearPairwiseSequenceMetric(settings=sequence_metric_settings)

# Linear metric settings
linear_metric.view_settings()

# %% [markdown]
# ### Demonstrate Metric Calculation Between Sequences
#
# Before applying clustering to the entire dataset, let's examine how our metrics quantify dissimilarity between specific patient pairs. This helps validate our metric choice and understand the clustering behavior.

# %%
# Select two patients for metric comparison
patient1_id = "10021487"
patient2_id = "10007795"

# Extract their admission sequences
seq1 = admissions_pool[patient1_id]
seq2 = admissions_pool[patient2_id]

# Colormap
colormap = {
    "EW EMER.": "blue",
    "DIRECT EMER.": "red",
    "ELECTIVE": "green",
    "URGENT": "black",
    "DIRECT OBKSERVATION": "purple",
}

# Visualize both sequences for comparison
# fmt: off
SequenceVisualizer.timeline() \
    .title(f"Patient {patient1_id} Admission Timeline") \
    .draw(seq1, entity_features=["admission_type"])
# fmt: on

# fmt: off
SequenceVisualizer.timeline() \
    .title(f"Patient {patient2_id} Admission Timeline") \
    .draw(seq2, entity_features=["admission_type"])
# fmt: on

# Calculate dissimilarity using our configured metric
dissimilarity = linear_metric(seq1, seq2)
print(f"\nSequence dissimilarity: {dissimilarity:.3f}")

# %% [markdown]
# ### Perform Hierarchical Clustering on Admission Sequences
#
# We apply hierarchical clustering to group patients with similar admission patterns. The clustering uses our configured dissimilarity metric to build a dendrogram and extract discrete patient clusters.

# %%
# Import hierarchical clustering components
from tanat.clustering import (
    HierarchicalClusterer,
    HierarchicalClustererSettings,
)

# Configure hierarchical clustering settings
clustering_settings = HierarchicalClustererSettings(
    metric=linear_metric,  # Use our configured sequence metric
    n_clusters=5,  # Target number of patient clusters
    cluster_column="trajectory_cluster",  # Column name for cluster assignments
)

# Initialize and fit the clustering model
clusterer = HierarchicalClusterer(settings=clustering_settings)
print("Fitting hierarchical clustering to admission sequences...")
clusterer.fit(admissions_pool)

# Display clustering summary
print("\nClustering Results:")
print(clusterer.summarize())

# %% [markdown]
# ### Analyze Clustering Results
#
# The clustering algorithm automatically augments our data with cluster assignments. Let's examine the distribution of patients across clusters and understand what the clustering has identified.

# %%
# Examine cluster assignments in the static data
print("Updated admissions pool with clustering results:")
print(admissions_pool)

# Access results dataframe
print("\nCluster stats:")
cluster_stats = admissions_pool.static_data["trajectory_cluster"].value_counts()
cluster_stats

# %% [markdown]
# ### Extract Specific Patient Clusters for Analysis
#
# We can filter patients by cluster to enable cluster-specific analysis. This is essential for comparing clinical outcomes and understanding the characteristics of each trajectory-based patient group.

# %%
# Import static filtering functionality
from tanat.criterion import StaticCriterion

# Extract cluster 1
cluster_id = 0

cluster_patients = admissions_pool.filter(
    StaticCriterion(query=f"trajectory_cluster == {cluster_id}"),
    level="sequence",
)

cluster_patients

# %% [markdown]
# ## 5. Survival Analysis Across Trajectory Clusters
#
# ### Clinical Outcome Comparison Methodology
#
# The ultimate validation of trajectory-based clustering is whether identified patient groups exhibit different clinical outcomes. We'll compare survival curves between clusters to assess whether admission patterns correlate with mortality risk.
#
# **Survival Analysis Approach:**
# 1. **Event Definition**: Use 'DEATH' admission type as mortality endpoint
# 2. **Time-to-Event**: Measure from trajectory start (T0) to death or censoring
# 3. **Cluster Comparison**: Compare Kaplan-Meier curves between largest clusters
# 4. **Clinical Interpretation**: Evaluate whether trajectory patterns predict survival outcomes
#
# This analysis demonstrates how temporal pattern recognition can potentially identify patients with different prognoses based on their care utilization patterns.

# %%
# Import survival analysis components
import matplotlib.pyplot as plt
from sksurv.nonparametric import kaplan_meier_estimator
from tanat.survival import SurvivalAnalysis

# Initialize survival analysis with Cox regression model
survival_analyzer = SurvivalAnalysis("coxnet")

survival_analyzer

# %% [markdown]
# ### Compare Survival Curves Between Trajectory Clusters
#
# We generate Kaplan-Meier survival curves for the two largest patient clusters to assess whether trajectory-based groupings correlate with differential mortality risk. Significant differences would suggest clinical relevance of the identified care patterns.

# %%
# Compare survival curves between the two largest clusters
plt.figure(figsize=(12, 8))

# Get the two largest clusters for comparison
top_clusters = cluster_stats.nlargest(2).index.tolist()
colors = ["blue", "red"]
cluster_labels = []

for i, cluster_id in enumerate(top_clusters):

    # Filter patients in this cluster
    cluster_patients = admissions_pool.filter(
        StaticCriterion(query=f"trajectory_cluster == {cluster_id}"), level="sequence"
    )

    # Construct survival data for this cluster
    survival_result = survival_analyzer.get_survival_array(
        sequence_pool=cluster_patients,
        query="admission_type == 'DEATH'",  # Death event definition
    )
    survival_data = survival_result.survival_array

    # Calculate Kaplan-Meier survival curve
    time_points, survival_probabilities = kaplan_meier_estimator(
        survival_data["observed"],  # Event occurrence (True = death observed)
        survival_data["duration"],  # Time to event or censoring
    )

    # Plot survival curve
    n_patients = len(cluster_patients.unique_ids)
    n_deaths = survival_data["observed"].sum()
    label = f"Cluster {cluster_id} (n={n_patients}, deaths={n_deaths})"
    cluster_labels.append(label)

    plt.step(
        time_points,
        survival_probabilities,
        where="post",
        color=colors[i],
        linewidth=2,
        label=label,
    )

# Configure plot
plt.title(
    "Kaplan-Meier Survival Curves by Trajectory Cluster", fontsize=14, fontweight="bold"
)
plt.xlabel("Time from Index Date (days)", fontsize=12)
plt.ylabel("Survival Probability", fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)
plt.ylim(0, 1.05)

# Add statistical summary
plt.figtext(
    0.02,
    0.02,
    "Note: Survival curves compare mortality risk between patient groups\n"
    "identified through trajectory-based clustering of admission patterns.",
    fontsize=9,
    style="italic",
)

plt.tight_layout()
plt.show()
