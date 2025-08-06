"""Message formatters for typo suggestions.

This module provides formatters that create user-friendly error messages
with typo suggestions in the style of Python 3.11+ error messages.
"""

from dataclasses import dataclass
from typing import Any

from .scope_analyzer import NameCandidate


@dataclass
class SuggestionMatch:
    """A potential typo correction match.

    Attributes:
        candidate: The name candidate that matches the target
        confidence: Confidence score from 0.0 to 1.0
        distance: Edit distance from target name
        algorithm: Algorithm used to find this match
    """

    candidate: NameCandidate
    confidence: float
    distance: int
    algorithm: str


class PythonStyleFormatter:
    """Formatter for creating Python 3.11+ style error messages with typo suggestions.

    Creates formatted error messages that include file location, source code
    highlighting, and helpful suggestions for fixing typos.

    Examples:
        >>> formatter = PythonStyleFormatter()
        >>> message = formatter.format_suggestion(
        ...     "self.speed", best_match, "game.py", {"class": "Hero", "method": "__init__"}
        ... )
        >>> print(message)
        File "game.py", line 21, in Hero.__init__
            self.sped = 300
            ^^^^^^^^^
        ValidationError: Required attribute 'self.speed' not found in Hero.__init__.
        Did you mean 'self.speed' instead of 'self.sped'?

        Note: This is a suggestion based on similarity analysis.
    """

    def format_suggestion_compact(
        self, target_name: str, best_match: SuggestionMatch, file_path: str, scope_config: dict[str, Any] | str
    ) -> str:
        """Format a compact typo suggestion in Russian for user display.

        Args:
            target_name: The name that was being searched for
            best_match: The best matching candidate found
            file_path: Path to the source file
            scope_config: Scope configuration for context

        Returns:
            Compact formatted suggestion message in Russian
        """
        candidate = best_match.candidate
        scope_context = self._format_scope_context_ru(scope_config)

        # Read source line for highlighting
        source_line = self._get_source_line(file_path, candidate.line_number)
        highlight = self._create_highlight(candidate.col_offset, candidate.end_col_offset)

        return f"""💡 Найдено похожее в {scope_context} (строка {candidate.line_number}):
{source_line}
{highlight}
Возможно, вы имели в виду '{target_name}' вместо '{candidate.name}'?"""

    def format_suggestion(
        self, target_name: str, best_match: SuggestionMatch, file_path: str, scope_config: dict[str, Any] | str
    ) -> str:
        """Format a typo suggestion in Python 3.11+ error style.

        Args:
            target_name: The name that was being searched for
            best_match: The best matching candidate found
            file_path: Path to the source file
            scope_config: Scope configuration for context

        Returns:
            Formatted error message with file location, source highlighting,
            and suggestion for correction
        """
        candidate = best_match.candidate
        scope_context = self._format_scope_context(scope_config)

        # Read source line for highlighting
        source_line = self._get_source_line(file_path, candidate.line_number)
        highlight = self._create_highlight(candidate.col_offset, candidate.end_col_offset)

        return f"""File "{file_path}", line {candidate.line_number}, in {scope_context}
    {source_line}
    {highlight}
ValidationError: Required attribute '{target_name}' not found in {scope_context}.
Did you mean '{target_name}' instead of '{candidate.name}'?

Note: This is a suggestion based on similarity analysis."""

    def format_debug_info(self, target_name: str, suggestions: list[SuggestionMatch]) -> str:
        """Format detailed debug information about typo analysis.

        Creates a detailed breakdown of all candidates considered and their
        similarity scores for debugging purposes.

        Args:
            target_name: The name that was being searched for
            suggestions: List of all suggestion matches found

        Returns:
            Formatted debug information string
        """
        if not suggestions:
            return f"DEBUG: No typo suggestions found for '{target_name}'"

        lines = [f"DEBUG: Typo analysis for '{target_name}':"]
        lines.append("  Found candidates:")

        for i, match in enumerate(suggestions[:5], 1):  # Limit to top 5
            confidence_desc = self._get_confidence_description(match.confidence)
            lines.append(
                f"    {i}. {match.candidate.name} "
                f"(distance: {match.distance}, line {match.candidate.line_number}, "
                f"confidence: {match.confidence:.2f}) - {confidence_desc}"
            )

        if suggestions:
            lines.append(f"  Selected: {suggestions[0].candidate.name} (highest confidence)")

        return "\n".join(lines)

    def _format_scope_context_ru(self, scope_config: dict[str, Any] | str) -> str:
        """Format scope configuration into a readable Russian context string.

        Args:
            scope_config: Scope configuration dict or string

        Returns:
            Human-readable scope context in Russian
        """
        if isinstance(scope_config, str):
            return "глобальной области" if scope_config == "global" else scope_config

        if "class" in scope_config and "method" in scope_config:
            return f"{scope_config['class']}.{scope_config['method']}"
        elif "class" in scope_config:
            return f"классе {scope_config['class']}"
        elif "function" in scope_config:
            return f"функции {scope_config['function']}"
        else:
            return "глобальной области"

    def _format_scope_context(self, scope_config: dict[str, Any] | str) -> str:
        """Format scope configuration into a readable context string.

        Args:
            scope_config: Scope configuration dict or string

        Returns:
            Human-readable scope context
        """
        if isinstance(scope_config, str):
            return scope_config if scope_config != "global" else "<module>"

        if "class" in scope_config and "method" in scope_config:
            return f"{scope_config['class']}.{scope_config['method']}"
        elif "class" in scope_config:
            return scope_config["class"]
        elif "function" in scope_config:
            return scope_config["function"]
        else:
            return "<module>"

    def _get_source_line(self, file_path: str, line_number: int) -> str:
        """Read the specified line from the source file.

        Args:
            file_path: Path to the source file
            line_number: Line number to read (1-based)

        Returns:
            The source line content, or placeholder if unavailable
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if 1 <= line_number <= len(lines):
                    return lines[line_number - 1].rstrip()
        except (IOError, IndexError, UnicodeDecodeError):
            pass
        return "<source unavailable>"

    def _create_highlight(self, start_col: int, end_col: int) -> str:
        """Create a highlight string with carets pointing to the problematic code.

        Args:
            start_col: Starting column position (0-based)
            end_col: Ending column position (0-based)

        Returns:
            String with spaces and carets for highlighting
        """
        spaces = " " * max(0, start_col)
        carets = "^" * max(1, end_col - start_col)
        return f"{spaces}{carets}"

    def _get_confidence_description(self, confidence: float) -> str:
        """Get a human-readable description of confidence level.

        Args:
            confidence: Confidence score from 0.0 to 1.0

        Returns:
            Human-readable confidence description
        """
        if confidence >= 0.9:
            return "most likely"
        elif confidence >= 0.7:
            return "likely"
        elif confidence >= 0.5:
            return "possible"
        else:
            return "less likely"
