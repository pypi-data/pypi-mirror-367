#! /usr/venv/bin python3
"""Clustering summarizer."""

import dataclasses

import numpy as np

from .base import BaseSummarizerMixin


@dataclasses.dataclass
class ClusterStats:
    """Data container for clusters statistics."""

    total: int
    avg_size: float
    min_size: int
    max_size: int


class ClusteringSummarizerMixin(BaseSummarizerMixin):
    """Implements summarization for cluster data."""

    def _format_statistics(self):
        """Generate cluster statistics section."""
        stats = self._calculate_stats()
        lines = [
            self._format_stat_line("Clusters", stats.total),
            self._format_stat_line("Avg size", f"{stats.avg_size:.1f}"),
            self._format_stat_line("Min size", stats.min_size),
            self._format_stat_line("Max size", stats.max_size),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate cluster breakdown and settings."""
        sections = []

        # Cluster details
        sections.append(f"{self.INDENT}Cluster Details:")
        if self.clusters is not None:
            sections.append(f"{self.INDENT * 2}{'ID':<15}{'Size':<10}")
            sections.append(f"{self.INDENT * 2}{'-' * 25}")

            for idx, cluster in enumerate(self.clusters, start=1):
                sections.append(f"{self.INDENT * 2}{idx:<15}{cluster.size:<10}")
        else:
            sections.append(f"{self.INDENT * 2}None")

        # Settings section
        sections.extend(
            [
                "",
                f"{self.INDENT}Settings:",
            ]
        )
        for key, value in self.settings.__dict__.items():
            sections.append(f"{self.INDENT * 2}{key:<20}{value}")

        return self._format_section("CLUSTER DETAILS", "\n".join(sections))

    def _calculate_stats(self):
        """Calculate basic statistics from cluster data."""
        if not self.clusters:
            return ClusterStats(total=0, avg_size=0.0, min_size=0, max_size=0)

        sizes = [cluster.size for cluster in self.clusters]
        return ClusterStats(
            total=len(self.clusters),
            avg_size=np.mean(sizes),
            min_size=np.min(sizes),
            max_size=np.max(sizes),
        )

    def get_compact_summary(self):
        """Generate compact summary for embedding in other summaries."""
        stats = self._calculate_stats()
        return [
            f"Total clusters: {stats.total}",
            f"Avg size: {stats.avg_size:.1f}",
            f"Size range: {stats.min_size}-{stats.max_size}",
        ]
