Examples Gallery
================

This gallery contains examples demonstrating TanaT's capabilities for temporal sequence analysis.
Each example focuses on a specific feature or use case, providing practical code that you can adapt for your own projects.

.. toctree::
   :hidden:

   01_containers/index
   02_criterion/index
   03_entity_metric/index
   04_sequence_metric/index
   05_trajectory_metric/index
   06_clustering/index
   07_sequence_viz/index
   08_survival/index

Data Containers
---------------

Learn how to work with TanaT's core data structures.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="01_containers/01_sequence.html" class="sphx-glr-thumbcontainer">
            <p><strong>Sequences</strong><br>
            Create, manipulate and analyze temporal sequences.</p>
        </a>
        
        <a href="01_containers/02_trajectory.html" class="sphx-glr-thumbcontainer">
            <p><strong>Trajectories</strong><br>
            Work with multi-sequence trajectories for complex data.</p>
        </a>
    </div>

Criteria and Filtering
----------------------

Examples of filtering and selecting data based on various criteria.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="02_criterion/01_query.html" class="sphx-glr-thumbcontainer">
            <p><strong>Query Criterion</strong><br>
            Filter sequences and trajectories using queries.</p>
        </a>
        
        <a href="02_criterion/02_static.html" class="sphx-glr-thumbcontainer">
            <p><strong>Static Criterion</strong><br>
            Apply criterion based on static features of individuals.</p>
        </a>
        
        <a href="02_criterion/03_time.html" class="sphx-glr-thumbcontainer">
            <p><strong>Temporal Criterion</strong><br>
            Filter data based on temporal patterns and time ranges.</p>
        </a>
        
        <a href="02_criterion/04_pattern.html" class="sphx-glr-thumbcontainer">
            <p><strong>Pattern Criterion</strong><br>
            Select sequences based on specific temporal patterns.</p>
        </a>
        
        <a href="02_criterion/05_length.html" class="sphx-glr-thumbcontainer">
            <p><strong>Length Criterion</strong><br>
            Filter sequences by their length.</p>
        </a>
    </div>

Distance Metrics
----------------

Learn about different distance metrics for measuring similarity between temporal data.

Entity Metrics
~~~~~~~~~~~~~~

Distance metrics for individual entities.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="03_entity_metric/01_hamming.html" class="sphx-glr-thumbcontainer">
            <p><strong>Hamming Distance</strong><br>
            Calculate Hamming distance between categorical entities.</p>
        </a>
    </div>

Sequence Metrics
~~~~~~~~~~~~~~~~

Distance metrics specifically designed for temporal sequences.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="04_sequence_metric/01_dtw.html" class="sphx-glr-thumbcontainer">
            <p><strong>Dynamic Time Warping</strong><br>
            Compute DTW distance between temporal sequences.</p>
        </a>
        
        <a href="04_sequence_metric/02_edit.html" class="sphx-glr-thumbcontainer">
            <p><strong>Edit Distance</strong><br>
            Calculate edit distance for sequence comparison.</p>
        </a>
        
        <a href="04_sequence_metric/03_lcp.html" class="sphx-glr-thumbcontainer">
            <p><strong>Common Prefix (LCP)</strong><br>
            Measure similarity using longest common prefix.</p>
        </a>
        
        <a href="04_sequence_metric/04_lcs.html" class="sphx-glr-thumbcontainer">
            <p><strong>Common Subsequence</strong><br>
            Distance from longest common subsequence.</p>
        </a>
        
        <a href="04_sequence_metric/05_linear_pairwise.html" class="sphx-glr-thumbcontainer">
            <p><strong>Linear Pairwise</strong><br>
            Efficient linear pairwise distance computation.</p>
        </a>
        
        <a href="04_sequence_metric/06_softdtw.html" class="sphx-glr-thumbcontainer">
            <p><strong>Soft DTW</strong><br>
            Differentiable version of DTW for machine learning.</p>
        </a>
        
        <a href="04_sequence_metric/07_custom.html" class="sphx-glr-thumbcontainer">
            <p><strong>Custom Sequence Metric</strong><br>
            Create your own custom metric for sequence analysis.</p>
        </a>
    </div>

Trajectory Metrics
~~~~~~~~~~~~~~~~~~

Distance metrics for multi-sequence trajectories.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="05_trajectory_metric/01_aggregation.html" class="sphx-glr-thumbcontainer">
            <p><strong>Aggregation Metric</strong><br>
            Aggregates sequence metrics for trajectory comparison.</p>
        </a>
        
        <a href="05_trajectory_metric/09_custom.html" class="sphx-glr-thumbcontainer">
            <p><strong>Custom Trajectory Metric</strong><br>
            Create your own custom metric for trajectory analysis.</p>
        </a>
    </div>


Clustering
----------------------

Examples of clustering algorithms applied directly to TanaT data containers.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="06_clustering/01_hierarchical.html" class="sphx-glr-thumbcontainer">
            <p><strong>Hierarchical clustering</strong><br>
            Perform hierarchical clustering on temporal data.</p>
        </a>
    
    </div>

Visualizations
----------------

Explore various visualization techniques for temporal sequences and trajectories.

Sequence visualizations
~~~~~~~~~~~~~~~~~~~~~~~

Visualizations for individual sequences or entire sequence pools.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="07_sequence_viz/01_timeline.html" class="sphx-glr-thumbcontainer">
            <p><strong>Timeline</strong><br>
            Visualize sequences as time-aligned timelines.</p>
        </a>

        <a href="07_sequence_viz/02_histogram.html" class="sphx-glr-thumbcontainer">
            <p><strong>Histogram</strong><br>
            Aggregate sequence values into time-based histograms.</p>
        </a>

        <a href="07_sequence_viz/03_distribution.html" class="sphx-glr-thumbcontainer">
            <p><strong>Distribution</strong><br>
            Show state proportions over time.</p>
        </a>
    </div>

Trajectory visualizations
~~~~~~~~~~~~~~~~~~~~~~~~~

Work in progress.

Survival Analysis
----------------------

Learn how to perform survival analysis directly from TanaT data containers.

.. raw:: html

    <div class="sphx-glr-gallery">
        <a href="08_survival/01_coxnet.html" class="sphx-glr-thumbcontainer">
            <p><strong>Cox model</strong><br>
            Predict survival probabilities using a Cox model.</p>
        </a>
        <a href="08_survival/02_tree.html" class="sphx-glr-thumbcontainer">
            <p><strong>Tree model</strong><br>
            Predict survival probabilities with a tree-based model.</p>
        </a>
    </div>


.. raw:: html

    <div class="sphx-glr-clear"></div>