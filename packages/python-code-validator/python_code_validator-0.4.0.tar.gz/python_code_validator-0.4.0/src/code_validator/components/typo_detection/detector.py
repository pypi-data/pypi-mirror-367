"""Main typo detection engine.

This module contains the core TypoDetector class that orchestrates the
typo detection process by analyzing failed searches and generating
helpful suggestions for users.
"""

import ast
from dataclasses import dataclass
from typing import Any

from .algorithms import LevenshteinDistance
from .formatters import PythonStyleFormatter, SuggestionMatch
from .scope_analyzer import NameCandidate, ScopeAnalyzer


@dataclass
class TypoSuggestion:
    """A complete typo suggestion with formatted message and debug info.

    Attributes:
        original_name: The name that was being searched for
        suggested_candidate: The best matching candidate, if any
        file_path: Path to the source file
        message: Formatted user-friendly message
        debug_info: Detailed debug information for logging
    """

    original_name: str
    suggested_candidate: SuggestionMatch | None
    file_path: str
    message: str
    debug_info: str

    @classmethod
    def empty(cls, original_name: str = "", file_path: str = "") -> "TypoSuggestion":
        """Create an empty suggestion when no matches are found.

        Args:
            original_name: The name that was searched for
            file_path: Path to the source file

        Returns:
            Empty TypoSuggestion instance
        """
        return cls(
            original_name=original_name,
            suggested_candidate=None,
            file_path=file_path,
            message="",
            debug_info=f"DEBUG: No typo suggestions found for '{original_name}'",
        )

    @property
    def has_suggestion(self) -> bool:
        """Check if this suggestion contains a valid recommendation.

        Returns:
            True if there's a suggested candidate, False otherwise
        """
        return self.suggested_candidate is not None


class TypoDetector:
    """Main typo detector for analyzing failed searches and suggesting corrections.

    Analyzes unsuccessful selector searches and provides intelligent suggestions
    based on similar names found in the same scope. Uses configurable similarity
    algorithms and confidence thresholds to ensure high-quality suggestions.

    Attributes:
        max_distance: Maximum edit distance to consider for suggestions
        min_confidence: Minimum confidence score to show suggestions
        scope_analyzer: Analyzer for extracting names from AST scopes
        message_formatter: Formatter for creating user-friendly messages
        similarity_algo: Algorithm for calculating string similarity

    Examples:
        >>> detector = TypoDetector()
        >>> suggestion = detector.analyze_failed_search(
        ...     "self.speed", {"class": "Hero", "method": "__init__"},
        ...     ast_tree, "game.py"
        ... )
        >>> if suggestion.has_suggestion:
        ...     print(suggestion.message)
    """

    def __init__(self, max_distance: int = 2, min_confidence: float = 0.6, max_candidates: int = 512):
        """Initialize the typo detector.

        Args:
            max_distance: Maximum Levenshtein distance to consider for suggestions
            min_confidence: Minimum confidence score (0.0-1.0) to show suggestions
            max_candidates: Maximum number of candidates to analyze per scope
        """
        self.max_distance = max_distance
        self.min_confidence = min_confidence
        self.scope_analyzer = ScopeAnalyzer(max_candidates=max_candidates)
        self.message_formatter = PythonStyleFormatter()
        self.similarity_algo = LevenshteinDistance()

    def analyze_failed_search(
        self,
        target_name: str,
        scope_config: dict[str, Any] | str,
        ast_tree: ast.Module,
        file_path: str,
        compact_mode: bool = True,
    ) -> TypoSuggestion:
        """Analyze a failed search and generate typo suggestions.

        When a selector fails to find a target name, this method analyzes
        all available names in the same scope and suggests the most likely
        intended name based on similarity metrics.

        Args:
            target_name: The name that was being searched for (e.g., 'self.speed')
            scope_config: Scope configuration dict ({'class': 'Hero', 'method': '__init__'})
                         or string ('global')
            ast_tree: The AST tree to search in
            file_path: Path to the source file for error reporting
            compact_mode: Mode for user-frendly output

        Returns:
            TypoSuggestion with the best match and formatted message, or empty
            suggestion if no good matches are found

        Examples:
            >>> detector = TypoDetector()
            >>> suggestion = detector.analyze_failed_search(
            ...     "self.speed", {"class": "Hero", "method": "__init__"},
            ...     tree, "hero.py"
            ... )
            >>> suggestion.has_suggestion
            True
            >>> "self.sped" in suggestion.message
            True
        """
        # Determine target type from the name
        target_type = self._infer_target_type(target_name)

        # Extract all available names in the scope
        candidates = self.scope_analyzer.extract_names_in_scope(ast_tree, scope_config, target_type)

        if not candidates:
            return TypoSuggestion.empty(target_name, file_path)

        # Find similar names using similarity algorithm
        suggestions = self._find_similar_names(target_name, candidates)

        # Create debug information
        debug_info = self.message_formatter.format_debug_info(target_name, suggestions)

        # Return best suggestion if it meets confidence threshold
        if suggestions and suggestions[0].confidence >= self.min_confidence:
            best_match = suggestions[0]
            if compact_mode:
                format_func = self.message_formatter.format_suggestion_compact
            else:
                format_func = self.message_formatter.format_suggestion
            message = format_func(target_name, best_match, file_path, scope_config)

            return TypoSuggestion(
                original_name=target_name,
                suggested_candidate=best_match,
                file_path=file_path,
                message=message,
                debug_info=debug_info,
            )

        return TypoSuggestion.empty(target_name, file_path)

    def _infer_target_type(self, target_name: str) -> str:
        """Infer the type of AST node to search for based on the target name.

        Args:
            target_name: The name being searched for

        Returns:
            Node type string ('assignment', 'function_def', 'class_def')
        """
        # Attributes (self.attr)
        if target_name.startswith("self."):
            return "assignment"
        # Class names (usually start with uppercase)
        elif target_name[0].isupper():
            return "class_def"
        # Constants/variables (ALL_CAPS or snake_case with underscores)
        elif target_name.isupper() or (target_name.islower() and "_" in target_name and not target_name.endswith("()")):
            # Check if it looks more like a function (has common function patterns)
            function_patterns = [
                "process",
                "init",
                "update",
                "render",
                "create",
                "delete",
                "get",
                "set",
                "run",
                "start",
                "stop",
            ]
            if any(pattern in target_name.lower() for pattern in function_patterns):
                return "function_def"
            return "assignment"
        # Function/method names (lowercase, simple names)
        elif target_name.islower():
            return "function_def"
        else:
            return "assignment"  # Default fallback

    def _find_similar_names(self, target: str, candidates: list[NameCandidate]) -> list[SuggestionMatch]:
        """Find and rank similar names from the candidate list.

        Args:
            target: The target name to find similarities for
            candidates: List of name candidates to compare against

        Returns:
            List of suggestion matches sorted by confidence (highest first)
        """
        matches = []

        for candidate in candidates:
            distance = self.similarity_algo.distance(target, candidate.name)

            # Skip candidates that are too different
            if distance > self.max_distance:
                continue

            # Calculate confidence score
            similarity = self.similarity_algo.similarity(target, candidate.name)
            confidence = self._calculate_confidence(target, candidate, similarity)

            matches.append(
                SuggestionMatch(candidate=candidate, confidence=confidence, distance=distance, algorithm="levenshtein")
            )

        # Sort by confidence (highest first), then by distance (lowest first)
        # This ensures that when confidence is equal, we prefer closer matches
        return sorted(matches, key=lambda m: (-m.confidence, m.distance))

    def _calculate_confidence(self, target: str, candidate: NameCandidate, similarity: float) -> float:
        """Calculate confidence score for a suggestion match.

        Combines similarity score with additional factors like name length,
        common prefixes, and contextual relevance.

        Args:
            target: The target name
            candidate: The candidate name
            similarity: Base similarity score from algorithm

        Returns:
            Adjusted confidence score (can exceed 1.0 for very good matches)
        """
        confidence = similarity

        # Strong boost for names with same prefix (e.g., self.speed vs self.sped)
        if "." in target and "." in candidate.name:
            target_prefix = target.split(".")[0]
            candidate_prefix = candidate.name.split(".")[0]
            if target_prefix == candidate_prefix:
                confidence += 0.15

        # Boost for similar word patterns and exact suffix matches
        target_parts = target.replace(".", "_").split("_")
        candidate_parts = candidate.name.replace(".", "_").split("_")

        # Very strong boost for exact suffix match (center_y vs centre_y - both end with _y)
        if len(target_parts) > 1 and len(candidate_parts) > 1:
            target_suffix = target_parts[-1]
            candidate_suffix = candidate_parts[-1]
            if target_suffix == candidate_suffix and len(target_suffix) > 0:
                confidence += 0.3  # Higher boost for semantic similarity

        # Check for similar word stems
        for t_part in target_parts:
            for c_part in candidate_parts:
                if len(t_part) > 3 and len(c_part) > 3:
                    # Check if words are similar (like center/centre)
                    part_similarity = self.similarity_algo.similarity(t_part, c_part)
                    if part_similarity > 0.7:
                        confidence += 0.1

        # Penalty for very different lengths
        len_diff = abs(len(target) - len(candidate.name))
        if len_diff > 4:
            confidence = max(0.0, confidence - 0.15)

        return confidence
