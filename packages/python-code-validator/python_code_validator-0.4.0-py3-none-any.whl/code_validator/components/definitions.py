"""Defines the core component interfaces for the validator using Protocols.

This module establishes the fundamental "contracts" for the main architectural
components: Rules, Selectors, and Constraints. By using `typing.Protocol`, we
ensure that any class conforming to these interfaces can be used interchangeably
by the system's factories and core engine. This enables a flexible and
decoupled plugin-style architecture, where new components can be added without
modifying the core logic.
"""

import ast
from typing import Protocol, runtime_checkable

from ..config import FullRuleConfig, ShortRuleConfig


@runtime_checkable
class Selector(Protocol):
    """An interface for objects that find and select specific nodes from an AST.

    A Selector's main responsibility is to traverse the Abstract Syntax Tree (AST)
    of a Python source file and return a list of nodes that match a specific
    criterion (e.g., all function definitions, all import statements).
    """

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Selects and returns a list of relevant AST nodes from the tree.

        Args:
            tree: The full, parsed AST of the source code to be searched.

        Returns:
            A list of ast.AST nodes that match the selector's criteria.
            An empty list should be returned if no matching nodes are found.
        """
        ...


@runtime_checkable
class Constraint(Protocol):
    """An interface for objects that apply a condition to a set of AST nodes.

    A Constraint takes the list of nodes found by a Selector and checks if they
    satisfy a specific condition (e.g., the list must not be empty, the node
    must inherit from a specific class).
    """

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if the given list of nodes satisfies the constraint.

        Args:
            nodes: A list of AST nodes provided by a Selector.

        Returns:
            True if the constraint is satisfied, False otherwise.
        """
        ...


@runtime_checkable
class Rule(Protocol):
    """An interface for any complete, executable validation rule.

    A Rule represents a single, self-contained validation check. It can be a
    "short" rule (like a linter check) or a "full" rule that internally uses
    a Selector and a Constraint. The core validator engine interacts with
    objects conforming to this protocol.

    Attributes:
        config: The dataclass object holding the configuration for this rule,
            parsed from the JSON file.
        typo_suggestion: Optional typo suggestion message for user display.
    """

    config: FullRuleConfig | ShortRuleConfig
    typo_suggestion: str | None

    def execute(self, tree: ast.Module | None, source_code: str | None = None) -> bool:
        """Executes the validation rule.

        Depending on the rule type, this method might operate on the AST, the
        raw source code, or both.

        Args:
            tree: The full AST of the source code (for structural checks).
            source_code: The raw source code string (e.g., for linter checks).

        Returns:
            True if the validation check passes, False otherwise.
        """
        ...
