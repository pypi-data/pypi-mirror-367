"""String similarity algorithms for typo detection.

This module implements various algorithms for measuring similarity between
strings to detect potential typos and suggest corrections.

Currently implemented:
    - Levenshtein Distance: For basic character insertions/deletions/substitutions
    - Future: Jaro-Winkler Distance for transpositions
"""

from typing import Protocol


class SimilarityAlgorithm(Protocol):
    """Protocol for string similarity algorithms."""

    def distance(self, s1: str, s2: str) -> int:
        """Calculate distance between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Distance value (lower = more similar)
        """
        ...

    def similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity score between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score from 0.0 (no similarity) to 1.0 (identical)
        """
        ...


class LevenshteinDistance:
    """Levenshtein distance algorithm for measuring string similarity.

    Calculates the minimum number of single-character edits (insertions,
    deletions, or substitutions) required to change one string into another.

    Examples:
        >>> algo = LevenshteinDistance()
        >>> algo.distance("speed", "sped")
        1
        >>> algo.similarity("speed", "sped")
        0.8
    """

    def distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings.

        Uses dynamic programming approach with O(n*m) time complexity
        and O(min(n,m)) space complexity optimization.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Minimum number of edits needed to transform s1 into s2
        """
        if not s1:
            return len(s2)
        if not s2:
            return len(s1)

        # Ensure s1 is the shorter string for space optimization
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        # Use only two rows instead of full matrix
        prev_row = list(range(len(s1) + 1))
        curr_row = [0] * (len(s1) + 1)

        for i in range(1, len(s2) + 1):
            curr_row[0] = i

            for j in range(1, len(s1) + 1):
                if s2[i - 1] == s1[j - 1]:
                    curr_row[j] = prev_row[j - 1]  # No operation needed
                else:
                    curr_row[j] = 1 + min(
                        prev_row[j],  # Deletion
                        curr_row[j - 1],  # Insertion
                        prev_row[j - 1],  # Substitution
                    )

            prev_row, curr_row = curr_row, prev_row

        return prev_row[len(s1)]

    def similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity score based on Levenshtein distance.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score from 0.0 to 1.0, where 1.0 means identical strings
        """
        if not s1 and not s2:
            return 1.0

        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0

        distance = self.distance(s1, s2)
        return 1.0 - (distance / max_len)
