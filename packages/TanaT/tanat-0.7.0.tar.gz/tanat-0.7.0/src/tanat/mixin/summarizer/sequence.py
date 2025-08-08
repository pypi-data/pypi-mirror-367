#! /usr/bin/env python3
"""
Sequence summarizer.
"""

import dataclasses

from .base import BaseSummarizerMixin


@dataclasses.dataclass
class SequenceStats:
    """Sequence statistics."""

    total: int
    avg_length: float
    min_length: int
    max_length: int
    vocab_size: int


class SequenceSummarizerMixin(BaseSummarizerMixin):
    """Sequence summarizer mixin."""

    def _format_statistics(self):
        """Generate sequence statistics section."""
        if self._is_pool:
            return self._format_pool_statistics()
        return self._format_single_statistics()

    def _format_pool_statistics(self):
        """Generate pool statistics."""
        stats = self._calculate_pool_stats()
        lines = [
            self._format_stat_line("Total sequences", stats.total),
            self._format_stat_line("Average length", f"{stats.avg_length:.1f}"),
            self._format_stat_line("Minimum length", stats.min_length),
            self._format_stat_line("Maximum length", stats.max_length),
            self._format_stat_line("Vocabulary size", stats.vocab_size),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_single_statistics(self):
        """Generate single sequence statistics."""
        lines = [
            self._format_stat_line("Sequence ID", str(self.id_value)),
            self._format_stat_line("Length", len(self)),
            self._format_stat_line("Vocabulary size", len(self.vocabulary)),
            self._format_stat_line("T0", str(self.t_zero)),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate data preview section."""
        sections = []

        # Sequence data preview
        sequence_sample = (
            self.sequence_data.head(3)
            .reset_index(drop=False, inplace=False)
            .to_string(index=False)
        )
        sections.append(f"{self.INDENT}Sequence Data:")
        sections.append(self._indent_text(sequence_sample, level=2))

        # Static data preview
        if self.static_data is not None:
            static_sample = (
                self.static_data.head(3)
                .reset_index(drop=False, inplace=False)
                .to_string(index=False)
            )
            sections.extend(
                [
                    "",
                    f"{self.INDENT}Static Data:",
                    self._indent_text(static_sample, level=2),
                ]
            )
        else:
            sections.extend(
                ["", f"{self.INDENT}Static Data:", f"{self.INDENT * 2}None"]
            )

        return self._format_section("DATA PREVIEW", "\n".join(sections))

    def _calculate_pool_stats(self):
        """Calculate sequence pool statistics."""
        sequences = self.get_sequences()
        if not sequences:
            return SequenceStats(0, 0.0, 0, 0, 0)

        lengths = [len(seq) for seq in sequences.values()]
        return SequenceStats(
            total=len(sequences),
            avg_length=sum(lengths) / len(lengths),
            min_length=min(lengths),
            max_length=max(lengths),
            vocab_size=len(self.vocabulary),
        )

    def get_compact_summary(self):
        """Generate compact summary for embedding in other summaries."""
        if self._is_pool:
            stats = self._calculate_pool_stats()
            return [
                f"Total sequences: {stats.total}",
                f"Avg length: {stats.avg_length:.1f}",
                f"Length range: {stats.min_length}-{stats.max_length}",
                f"Vocab size: {stats.vocab_size}",
            ]
        return [f"Length: {len(self)}", f"Vocab size: {len(self.vocabulary)}"]
