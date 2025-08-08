#! /usr/bin/env python3
"""
Trajectory summarizer.
"""

from .base import BaseSummarizerMixin


class TrajectorySummarizerMixin(BaseSummarizerMixin):
    """Trajectory summarizer mixin."""

    def _format_statistics(self):
        """Generate trajectory statistics section."""
        if self._is_pool:
            return self._format_pool_statistics()
        return self._format_single_statistics()

    def _format_pool_statistics(self):
        """Generate pool statistics."""
        sequence_names = list(self.sequence_pools.keys())
        display_names = self._format_names(sequence_names)

        lines = [
            self._format_stat_line("Total trajectories", len(self.unique_ids)),
            self._format_stat_line("Sequence types", len(sequence_names)),
            self._format_stat_line("Sequence names", display_names),
            self._format_stat_line(
                "Intersection mode", str(self.settings.intersection)
            ),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_single_statistics(self):
        """Generate single trajectory statistics."""
        sequence_names = list(self.sequences.keys())
        display_names = self._format_names(sequence_names)

        lines = [
            self._format_stat_line("Trajectory ID", str(self.id_value)),
            self._format_stat_line("Sequence count", len(sequence_names)),
            self._format_stat_line("Sequence names", display_names),
            self._format_stat_line("T0", str(self.t_zero)),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate trajectory data preview."""
        sections = []

        # Static data
        if self.static_data is not None:
            static_sample = (
                self.static_data.head(3)
                .reset_index(drop=False, inplace=False)
                .to_string(index=False)
            )
            sections.extend(
                [
                    f"{self.INDENT}Static Data:",
                    self._indent_text(static_sample, level=2),
                    "",
                ]
            )

        # Sequence data
        sequences = self.sequence_pools if self._is_pool else self.sequences
        sections.append(f"{self.INDENT}Sequence Data:")

        for name, seq_obj in sequences.items():
            sections.append(f"{self.INDENT * 2}> {name}")
            compact_info = seq_obj.get_compact_summary()
            for info in compact_info:
                sections.append(f"{self.INDENT * 3}{info}")
            sections.append("")  # Spacing between sequences

        # Remove last empty line
        if sections and sections[-1] == "":
            sections.pop()

        return self._format_section("DATA PREVIEW", "\n".join(sections))

    def _format_names(self, names, max_display=3):
        """Format sequence names with truncation if needed."""
        if len(names) <= max_display:
            return ", ".join(names)
        return ", ".join(names[:max_display]) + f" (+{len(names) - max_display} more)"
