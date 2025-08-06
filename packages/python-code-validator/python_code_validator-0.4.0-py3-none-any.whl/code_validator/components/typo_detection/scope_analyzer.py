"""Scope analysis for extracting names from AST nodes.

This module provides functionality to extract all names of a specific type
(assignments, function definitions, class definitions) from a given scope
in the AST, preserving location information for error reporting.
"""

import ast
from dataclasses import dataclass
from typing import Any

from ..ast_utils import get_full_name


@dataclass
class NameCandidate:
    """A candidate name found in the AST with location information.

    Attributes:
        name: The full name (e.g., 'self.speed', 'my_function')
        line_number: Line number in the source file (1-based)
        col_offset: Column offset of the name start (0-based)
        end_col_offset: Column offset of the name end (0-based)
        scope: String representation of the scope where name was found
        node_type: Type of AST node ('assignment', 'function_def', 'class_def')
        node: Reference to the actual AST node for additional analysis
    """

    name: str
    line_number: int
    col_offset: int
    end_col_offset: int
    scope: str
    node_type: str
    node: ast.AST


class ScopeAnalyzer:
    """Analyzer for extracting names from specific scopes in AST.

    Extracts all names of specified types (assignments, functions, classes)
    from a given scope while preserving location information needed for
    error reporting and typo suggestions.

    Attributes:
        max_candidates: Maximum number of candidates to extract (performance limit)
        _extractors: Dictionary mapping node types to extraction methods
    """

    def __init__(self, max_candidates: int = 512):
        """Initialize the scope analyzer.

        Args:
            max_candidates: Maximum number of candidates to extract to prevent
                performance issues with very large scopes
        """
        self.max_candidates = max_candidates
        self._extractors = {
            "assignment": self._extract_assignments,
            "function_def": self._extract_function_defs,
            "class_def": self._extract_class_defs,
        }

    def extract_names_in_scope(
        self, tree: ast.Module, scope_config: dict[str, Any] | str, target_type: str
    ) -> list[NameCandidate]:
        """Extract all names of specified type from the given scope.

        Args:
            tree: The AST tree to search in
            scope_config: Scope configuration dict ({'class': 'Hero', 'method': '__init__'})
                         or string ('global')
            target_type: Type of names to extract ('assignment', 'function_def', 'class_def')

        Returns:
            List of name candidates found in the scope, limited by max_candidates

        Examples:
            >>> analyzer = ScopeAnalyzer()
            >>> candidates = analyzer.extract_names_in_scope(
            ...     tree, {'class': 'Hero', 'method': '__init__'}, 'assignment'
            ... )
            >>> [c.name for c in candidates]
            ['self.scale', 'self.sped', 'self.health']
        """
        from ..scope_handler import find_scope_node

        # Find the target scope in AST
        if scope_config == "global":
            scope_node = tree
        else:
            scope_node = find_scope_node(tree, scope_config)
            if not scope_node:
                return []

        # Extract names using appropriate extractor
        extractor = self._extractors.get(target_type, self._extract_all)
        candidates = extractor(scope_node, scope_config)

        # Limit results to prevent performance issues
        return candidates[: self.max_candidates]

    def _extract_assignments(self, scope_node: ast.AST, scope_config: dict[str, Any] | str) -> list[NameCandidate]:
        """Extract all assignment targets from the scope.

        Handles both regular assignments (x = 5) and annotated assignments (x: int = 5).

        Args:
            scope_node: AST node representing the scope to search in
            scope_config: Scope configuration for context

        Returns:
            List of assignment name candidates
        """
        candidates = []

        for node in ast.walk(scope_node):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                # Handle multiple targets in assignments like a = b = 5
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]

                for target in targets:
                    name = get_full_name(target)
                    if name:
                        candidates.append(
                            NameCandidate(
                                name=name,
                                line_number=target.lineno,
                                col_offset=target.col_offset,
                                end_col_offset=getattr(target, "end_col_offset", target.col_offset + len(name)),
                                scope=str(scope_config),
                                node_type="assignment",
                                node=target,
                            )
                        )

        return candidates

    def _extract_function_defs(self, scope_node: ast.AST, scope_config: dict[str, Any] | str) -> list[NameCandidate]:
        """Extract all function definition names from the scope.

        Args:
            scope_node: AST node representing the scope to search in
            scope_config: Scope configuration for context

        Returns:
            List of function name candidates
        """
        candidates = []

        for node in ast.walk(scope_node):
            if isinstance(node, ast.FunctionDef):
                candidates.append(
                    NameCandidate(
                        name=node.name,
                        line_number=node.lineno,
                        col_offset=node.col_offset,
                        end_col_offset=getattr(node, "end_col_offset", node.col_offset + len(node.name)),
                        scope=str(scope_config),
                        node_type="function_def",
                        node=node,
                    )
                )

        return candidates

    def _extract_class_defs(self, scope_node: ast.AST, scope_config: dict[str, Any] | str) -> list[NameCandidate]:
        """Extract all class definition names from the scope.

        Args:
            scope_node: AST node representing the scope to search in
            scope_config: Scope configuration for context

        Returns:
            List of class name candidates
        """
        candidates = []

        for node in ast.walk(scope_node):
            if isinstance(node, ast.ClassDef):
                candidates.append(
                    NameCandidate(
                        name=node.name,
                        line_number=node.lineno,
                        col_offset=node.col_offset,
                        end_col_offset=getattr(node, "end_col_offset", node.col_offset + len(node.name)),
                        scope=str(scope_config),
                        node_type="class_def",
                        node=node,
                    )
                )

        return candidates

    def _extract_all(self, scope_node: ast.AST, scope_config: dict[str, Any] | str) -> list[NameCandidate]:
        """Extract all types of names from the scope.

        Fallback method that extracts assignments, functions, and classes.

        Args:
            scope_node: AST node representing the scope to search in
            scope_config: Scope configuration for context

        Returns:
            List of all name candidates found
        """
        candidates = []
        candidates.extend(self._extract_assignments(scope_node, scope_config))
        candidates.extend(self._extract_function_defs(scope_node, scope_config))
        candidates.extend(self._extract_class_defs(scope_node, scope_config))
        return candidates
