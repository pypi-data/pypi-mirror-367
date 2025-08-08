# TanaT
**Temporal Analysis of Trajectories**

*TanaT* is a powerful Python library designed for advanced temporal sequence analysis, with specialized focus on patient care pathways and complex temporal data structures (trajectories).

## What Makes TanaT Different

TanaT bridges the gap between traditional time series analysis and complex temporal sequence modeling by offering:

- **Expressive Data Representation**: Handle event sequences, interval sequences, and state sequences with unified APIs
- **Advanced Distance Metrics**: Specialized metrics for temporal data including DTW, edit distance, and custom metrics
- **Flexible Clustering**: State-of-the-art clustering algorithms adapted for temporal sequences and trajectories
- **Extensible Architecture**: Modular design allowing easy integration of new methods and metrics

## Core Capabilities

### Data Structures
- **Event Sequences**: Point-in-time events with rich feature descriptions
- **Interval Sequences**: Time-spanning events with overlapping support
- **State Sequences**: Continuous state representations with temporal transitions
- **Trajectories**: Multi-dimensional temporal data combining multiple sequence types

### Analysis Methods
- **Distance Computation**: Dynamic Time Warping, Edit Distance, Longest Common Subsequence, and more
- **Clustering**: Specialized algorithms for grouping similar temporal patterns
- **Filtering & Selection**: Advanced criteria-based data selection and manipulation
- **Visualization**: Comprehensive tools for temporal data exploration
- **Survival analysis**: Model and predict time until key events

## Scientific Foundation

TanaT draws inspiration from established frameworks:

- **TraMineR** (R): State sequence analysis methodologies
- **aeon** & **tslearn**: Time series analysis best practices

## Development Status

**Current Version**: 0.7.0 (Preliminary Release)
- Core architecture completed
- Ready for beta testing and community feedback

## Architecture Overview

<img src="doc/source/static/tanat_ecosystem.png" alt="TanaT Ecosystem" width="100%"/>

## Resources

- **Documentation**: [Full Documentation](https://gitlab.inria.fr/tanat/core/tanat)
- **Source Code**: [GitLab Repository](https://gitlab.inria.fr/tanat/core/tanat.git)
- **Issues & Support**: [Issue Tracker](https://gitlab.inria.fr/tanat/core/tanat/-/issues)
- **Packages**: [GitLab Registry](https://gitlab.inria.fr/tanat/core/tanat/-/packages)

## Citation

If you use TanaT in your research, please cite:

```bibtex
@inproceedings{tanat2025,
title={Towards a Library for the Analysis of Temporal Sequences},
authors={Thomas Guyet and Arnaud Duvermy},
booktitle={Proceedings of AALTD, ECML Workshop on Advanced Analytics and Learning on Temporal Data},
year={2025},
pages={16}
}
```


## Affiliation & Support

TanaT is developed as part of the [AIRacles Chair](https://www.bernoulli-lab.fr/project/chaire-ai-racles/) (Inria/APHP) within the [AIstroSight](https://team.inria.fr/aistrosight/) Inria research team, focusing on AI applications in healthcare and temporal data analysis.

## Team

**Core Development Team**
- **Arnaud Duvermy** - Architecture & Core Development
- **Thomas Guyet** - Project Leadership & Research Methods

**Contact**: [TanaT](mailto:tanat@inria.fr)

This work benefits from the advice of Mike Rye.

---
*TanaT is open source software designed to advance temporal sequence analysis in research and industry applications.*
