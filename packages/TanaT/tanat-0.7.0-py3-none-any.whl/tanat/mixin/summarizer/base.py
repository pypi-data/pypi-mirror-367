#!/usr/bin/env python3
"""
Summarizer utilities.
"""

from abc import abstractmethod
import logging
from pathlib import Path

from pypassist.utils.export import export_string

LOGGER = logging.getLogger(__name__)


class BaseSummarizerMixin:
    """Base class for generating summaries."""

    # Constantes de formatage centralisées
    SECTION_WIDTH = 50
    BORDER_CHAR = "─"
    INDENT = "  "

    @property
    def statistics(self):
        """Generate statistics section."""
        return self._format_statistics()

    @property
    def summary(self):
        """Generate a formatted summary and return it."""
        return self.summarize()

    def summarize(self, export_to=None, *, filename="summary.txt"):
        """
        Generate a formatted summary with optional file export.

        Args:
            export_to (str): Path to export the summary to.
            filename (str): Name of the file to export the summary to.

        Returns:
            str or None: The formatted summary text (or None if exported).
        """
        sections = [
            self._format_header(),
            self._format_statistics(),
            self._format_data_preview(),
        ]

        summary_text = "\n".join(filter(None, sections))

        if export_to:
            full_path = Path(export_to) / filename
            export_string(summary_text, full_path)
            return None
        return summary_text

    def _format_header(self):
        """Generate a clean, consistent header."""
        title = self._get_title()
        border = self.BORDER_CHAR * self.SECTION_WIDTH
        return f"┌{border}┐\n│ {title:<{self.SECTION_WIDTH-2}} │\n└{border}┘"

    def _get_title(self):
        """Get the summary title."""
        return f"{self.__class__.__name__} summary"

    def _format_section(self, title, content):
        """Format a section with consistent styling."""
        if not content:
            return ""
        separator = self.BORDER_CHAR * (self.SECTION_WIDTH // 2)
        return f"\n{title}\n{separator}\n{content}"

    def _format_stat_line(self, label, value):
        """Format a single statistics line."""
        # total_width = self.SECTION_WIDTH // 2 - len(self.INDENT)
        width = (self.SECTION_WIDTH - len(self.INDENT)) // 2
        label_width = width - 5
        return f"{self.INDENT}{label:<{label_width}}{value:<15}"

    def _indent_text(self, text, level=1):
        """Indent text consistently."""
        indent = self.INDENT * level
        return "\n".join(f"{indent}{line}" for line in text.splitlines())

    @abstractmethod
    def _format_statistics(self):
        """Generate statistics section. Must be implemented by child classes."""

    @abstractmethod
    def _format_data_preview(self):
        """Generate data preview section. Must be implemented by child classes."""
