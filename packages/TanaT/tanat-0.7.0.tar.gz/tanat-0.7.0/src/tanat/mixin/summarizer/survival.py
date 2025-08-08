#!/usr/bin/env python3
"""Survival analysis summarizer."""

import dataclasses
from .base import BaseSummarizerMixin


@dataclasses.dataclass
class SurvivalStats:
    """Data container for survival statistics."""

    total_sequences: int
    observed_events: int
    censored_events: int
    censoring_rate: float
    mean_duration: float
    median_duration: float
    duration_std: float


class SurvivalSummarizerMixin(BaseSummarizerMixin):
    """Summarization mixin for survival analysis."""

    def _get_title(self):
        """Get the summary title."""
        return f"Survival Analysis ({self.model_type}) Summary"

    def _format_statistics(self):
        """Generate survival statistics section."""
        if not hasattr(self, "_last_result") or self._last_result is None:
            lines = [
                self._format_stat_line("Status", "No analysis performed yet"),
                self._format_stat_line("Model type", self.model_type),
            ]
        else:
            stats = self._calculate_stats()
            lines = [
                self._format_stat_line("Model type", self.model_type),
                self._format_stat_line("Total sequences", stats.total_sequences),
                self._format_stat_line("Observed events", stats.observed_events),
                self._format_stat_line("Censored events", stats.censored_events),
                self._format_stat_line(
                    "Censoring rate", f"{stats.censoring_rate:.1f}%"
                ),
                self._format_stat_line("Mean duration", f"{stats.mean_duration:.2f}"),
                self._format_stat_line(
                    "Median duration", f"{stats.median_duration:.2f}"
                ),
            ]

        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate survival data preview."""
        sections = []

        # Model settings
        sections.append(f"{self.INDENT}Model Settings:")
        settings_dict = (
            self.settings.__dict__ if hasattr(self.settings, "__dict__") else {}
        )
        for key, value in settings_dict.items():
            if not key.startswith("_"):
                sections.append(f"{self.INDENT * 2}{key:<20}{value}")

        if hasattr(self, "_last_result") and self._last_result is not None:
            sections.extend(
                [
                    "",
                    f"{self.INDENT}Duration Statistics:",
                    f"{self.INDENT * 2}Min: {self._last_result.durations.min():.2f}",
                    f"{self.INDENT * 2}25%: {self._last_result.durations.quantile(0.25):.2f}",
                    f"{self.INDENT * 2}75%: {self._last_result.durations.quantile(0.75):.2f}",
                    f"{self.INDENT * 2}Max: {self._last_result.durations.max():.2f}",
                ]
            )

        return self._format_section("MODEL & DATA DETAILS", "\n".join(sections))

    def _calculate_stats(self):
        """Calculate statistics from last result."""
        result = self._last_result
        n_observed = result.observation_data["observed"].sum()
        n_total = len(result.observation_data)
        n_censored = n_total - n_observed

        return SurvivalStats(
            total_sequences=n_total,
            observed_events=n_observed,
            censored_events=n_censored,
            censoring_rate=(n_censored / n_total) * 100,
            mean_duration=result.durations.mean(),
            median_duration=result.durations.median(),
            duration_std=result.durations.std(),
        )

    def get_compact_summary(self):
        """Generate compact summary for embedding in other summaries."""
        if not hasattr(self, "_last_result") or self._last_result is None:
            return [f"Model: {self.model_type}", "Status: No analysis performed"]

        stats = self._calculate_stats()
        return [
            f"Model: {self.model_type}",
            f"Sequences: {stats.total_sequences}",
            f"Observed: {stats.observed_events}",
            f"Censoring: {stats.censoring_rate:.1f}%",
            f"Mean duration: {stats.mean_duration:.2f}",
        ]
