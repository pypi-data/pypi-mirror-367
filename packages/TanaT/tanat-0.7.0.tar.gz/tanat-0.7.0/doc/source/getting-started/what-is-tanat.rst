What is TanaT?
==============

*TanaT* (*Temporal ANalysis of Trajectories*) is an extensible Python library for temporal sequence analysis with a primary focus on patient care pathways.

The name also refers to a variety of wine grape that originates from south of France, taking continuity with the `TraMineR library <http://traminer.unige.ch/>`_ which widely inspired this work (Traminer is also a variety of wine grape).

Key Features
------------

**Expressive Data Representation**
    TanaT provides a very expressive and flexible representation of event-based temporal data, distinguishing between entities, sequences, and trajectories.

**Multiple Sequence Types**
    Support for event sequences (point-in-time), interval sequences (duration-based), and state sequences (continuous states).

**Advanced Analytics**
    Implements different metrics and clustering algorithms specifically designed for temporal sequence data.

**Extensible Architecture**
    Built with extensibility in mind, making it easy to add new metrics, clustering methods, and analysis techniques.

What Makes TanaT Different?
---------------------------

Unlike traditional time series libraries, TanaT is designed for **irregularly sampled, symbolic event-based temporal data**. 
We classify timed sequences data as *non-euclidean* in the sense that there is no natural euclidean space to represent collections of timed sequences.

For instance:

* Timed sequences in a pool don't necessarily have the same length (same number of events)
* Events themselves have no natural euclidean representation (when using symbolic event types)
* Traditional data analysis methods don't apply directly to these *non-euclidean* data

TanaT Ecosystem
---------------

.. image:: ../static/tanat_ecosystem.png
   :align: center
   :alt: TanaT Ecosystem Overview

The TanaT ecosystem provides a complete workflow for temporal sequence analysis, from data ingestion to advanced analytics and visualization.

Inspiration and Related Work
----------------------------

TanaT has been strongly inspired by:

* The `TraMineR <http://traminer.unige.ch/>`_ library for the analysis of state sequences in R
* Libraries dedicated to time series analysis such as `aeon <https://www.aeon-toolkit.org/>`_ and `tslearn <https://tslearn.readthedocs.io/>`_

Development Status
------------------

TanaT is actively developed as part of the `AIRacles Chair <https://www.bernoulli-lab.fr/project/chaire-ai-racles/>`_ 
(Inria/APHP) in the `AIstroSight <https://team.inria.fr/aistrosight/>`_ Inria Team.

Roadmap
~~~~~~~

- **Project start:** June 2024  
- **Preliminary release (v0.7.0):** August 2025  
  Core architecture completed and ready for beta testing.

Contributors and Contact
------------------------

This development is part of the `AIRacles Chair <https://www.bernoulli-lab.fr/project/chaire-ai-racles/>`_ (Inria/APHP) 
and is conducted in the `AIstroSight <https://team.inria.fr/aistrosight/>`_ Inria Team.

**Core Team:**

- Arnaud Duvermy (design, core architecture, maintenance)  
- Thomas Guyet (project leader, design, development of data analysis methods, documentation)

**Contact:** tanat@inria.fr

This work benefits from the advice of Mike Rye.

Links
-----

* `Homepage <https://gitlab.inria.fr/tanat/core/tanat>`_
* `Source Code <https://gitlab.inria.fr/tanat/core/tanat.git>`_
* `Issues <https://gitlab.inria.fr/tanat/core/tanat/-/issues>`_
* `GitLab Package Registry <https://gitlab.inria.fr/tanat/core/tanat/-/packages>`_
