"""Contains concrete implementations of all Constraint components.

Each class in this module implements the `Constraint` protocol and encapsulates
the logic for a specific condition that can be checked against a list of
AST nodes. These classes are instantiated by the `ConstraintFactory` based on
the "constraint" block in a JSON rule.

The module also includes helper functions for processing AST nodes, which are
used internally by the constraint classes.
"""

import ast
from typing import Any

from .. import LogLevel
from ..components.ast_utils import get_full_name
from ..components.definitions import Constraint
from ..output import log_initialization


class IsRequiredConstraint(Constraint):
    """Checks that at least one node was found by the selector.

    This constraint is used to enforce the presence of a required language
    construct. It can also check for an exact number of occurrences.

    Supports smart typo detection when no nodes are found - analyzes similar
    names in the same scope and provides helpful suggestions.

    JSON Params:
        count (int, optional): If provided, checks if the number of found
            nodes is exactly equal to this value.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the constraint.

        Args:
            **kwargs: Configuration for the constraint, e.g., 'count'.
        """
        self.expected_count = kwargs.get("count")
        self._typo_detector = None  # Lazy initialization

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if the list of nodes is not empty or matches expected count."""
        if self.expected_count is not None:
            return len(nodes) == self.expected_count
        return len(nodes) > 0

    def check_with_context(
        self,
        nodes: list[ast.AST],
        target_name: str,
        scope_config: dict[str, Any] | str,
        ast_tree: ast.Module,
        file_path: str,
        console,
    ) -> tuple[bool, str | None]:
        """Enhanced check with typo detection support.

        Performs the standard constraint check, and if it fails due to no nodes
        being found, analyzes potential typos and provides helpful suggestions.

        Args:
            nodes: List of AST nodes found by the selector
            target_name: The name that was being searched for
            scope_config: Scope configuration for the search
            ast_tree: The complete AST tree for analysis
            file_path: Path to the source file
            console: Console instance for output

        Returns:
            Tuple of (constraint_result, typo_suggestion_message)
        """
        # Perform standard check first
        standard_result = self.check(nodes)

        # If check fails and no nodes found, try typo detection
        if not standard_result and len(nodes) == 0 and target_name:
            typo_suggestion = self._analyze_typo_and_suggest(target_name, scope_config, ast_tree, file_path, console)
            return standard_result, typo_suggestion

        return standard_result, None

    def _analyze_typo_and_suggest(
        self, target_name: str, scope_config: dict[str, Any] | str, ast_tree: ast.Module, file_path: str, console
    ) -> str | None:
        """Analyze potential typos and return suggestion message.

        Args:
            target_name: The name that was being searched for
            scope_config: Scope configuration for the search
            ast_tree: The complete AST tree for analysis
            file_path: Path to the source file
            console: Console instance for output

        Returns:
            User-friendly typo suggestion message or None if no suggestion
        """
        try:
            # Lazy import to avoid circular dependencies
            if self._typo_detector is None:
                from ..components.typo_detection import TypoDetector

                self._typo_detector = TypoDetector()

            # Analyze failed search for typos
            suggestion = self._typo_detector.analyze_failed_search(target_name, scope_config, ast_tree, file_path)

            # Log debug information
            console.print(suggestion.debug_info, level=LogLevel.DEBUG)

            # If we have a good suggestion, return full formatted message
            if suggestion.has_suggestion:
                # Log detailed suggestion for debugging
                console.print(f"Typo suggestion: {suggestion.message}", level=LogLevel.INFO)

                # Return full formatted message for user display
                return suggestion.message

        except Exception as e:
            # Don't let typo detection break the main validation
            console.print(f"Typo detection failed: {e}", level=LogLevel.DEBUG)

        return None


class IsForbiddenConstraint(Constraint):
    """Checks that no nodes were found by the selector.

    This is the inverse of `IsRequiredConstraint` and is used to forbid certain
    constructs, such as specific function calls or imports.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the constraint."""
        pass

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if the list of nodes is empty."""
        return not nodes


class MustInheritFromConstraint(Constraint):
    """Checks that a ClassDef node inherits from a specific parent class.

    This constraint is designed to work with a selector that returns a single
    `ast.ClassDef` node. It can resolve both simple names (e.g., `Exception`)
    and attribute-based names (e.g., `arcade.Window`).

    JSON Params:
        parent_name (str): The expected name of the parent class.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the constraint.

        Args:
            **kwargs: Keyword arguments from the JSON rule's constraint config.
                Expects `parent_name` (str) specifying the required parent class.
        """
        self.parent_name_to_find: str | None = kwargs.get("parent_name")

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if the found class node inherits from the specified parent."""
        if not self.parent_name_to_find or len(nodes) != 1:
            return False

        node = nodes[0]
        if not isinstance(node, ast.ClassDef):
            return False

        for base in node.bases:
            full_name = self._get_full_attribute_name(base)
            if full_name == self.parent_name_to_find:
                return True
        return False

    @staticmethod
    def _get_full_attribute_name(node: ast.AST) -> str | None:
        """Recursively builds the full attribute name from a base class node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = MustInheritFromConstraint._get_full_attribute_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return None


class MustBeTypeConstraint(Constraint):
    """Checks the type of the value in an assignment statement.

    It works for simple literals (numbers, strings, lists, etc.) and for
    calls to built-in type constructors (e.g., `list()`, `dict()`).

    JSON Params:
        expected_type (str): The name of the type, e.g., "str", "int", "list".
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the constraint.

        Args:
            **kwargs: Keyword arguments from the JSON rule's constraint config.
                Expects `expected_type` (str) with the name of the required type.
        """
        self.expected_type_str: str | None = kwargs.get("expected_type")
        self.type_map = {
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "bool": bool,
            "set": set,
            "tuple": tuple,
        }
        self.constructor_map = {t: t for t in self.type_map}

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if the assigned value has the expected Python type."""
        if not nodes or not self.expected_type_str:
            return False
        expected_py_type = self.type_map.get(self.expected_type_str)
        if not expected_py_type:
            return False

        for node in nodes:
            value_node = getattr(node, "value", None)
            if value_node is None:
                continue

            if self._is_correct_type(value_node, expected_py_type):
                continue
            return False
        return True

    def _is_correct_type(self, value_node: ast.AST, expected_py_type: type) -> bool:
        """Checks a single value node against the expected type."""
        try:
            assigned_value = ast.literal_eval(value_node)
            if isinstance(assigned_value, expected_py_type):
                return True
        except (ValueError, TypeError, SyntaxError):
            pass

        if isinstance(value_node, ast.Call):
            func_name = getattr(value_node.func, "id", None)
            expected_constructor = self.constructor_map.get(self.expected_type_str)
            if func_name == expected_constructor:
                return True
        return False


class NameMustBeInConstraint(Constraint):
    """Checks if the name of a found node is in an allowed list of names.

    This is useful for rules like restricting global variables to a pre-defined
    set of constants.

    JSON Params:
        allowed_names (list[str]): A list of strings containing the allowed names.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the constraint.

        Args:
            **kwargs: Keyword arguments from the JSON rule's constraint config.
                Expects `allowed_names` (list[str]) containing the valid names.
        """
        self.allowed_names = set(kwargs.get("allowed_names", []))

    @staticmethod
    def _get_name(node: ast.AST) -> str | None:
        """Gets a name from various node types."""
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            return get_full_name(target)
        return getattr(node, "name", getattr(node, "id", None))

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if all found node names are in the allowed set."""
        for node in nodes:
            name_to_check = self._get_name(node)
            if name_to_check and name_to_check not in self.allowed_names:
                return False
        return True


class ValueMustBeInConstraint(Constraint):
    """Checks if the value of a found literal node is in an allowed list.

    This is primarily used to check for "magic numbers" or "magic strings",
    allowing only a specific set of literal values to be present.

    JSON Params:
        allowed_values (list): A list of allowed literal values (e.g., [0, 1]).
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the constraint.

        Args:
            **kwargs: Keyword arguments from the JSON rule's constraint config.
                Expects `allowed_values` (list) containing the valid literal values.
        """
        self.allowed_values = set(kwargs.get("allowed_values", []))

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if all found literal values are in the allowed set."""
        if not self.allowed_values:
            return not nodes

        for node in nodes:
            if isinstance(node, ast.Constant):
                if node.value not in self.allowed_values:
                    return False
            else:
                return False
        return True


class MustHaveArgsConstraint(Constraint):
    """Checks that a FunctionDef node has a specific signature.

    This constraint can check for an exact number of arguments or for an
    exact sequence of argument names, ignoring `self` or `cls` in methods.

    JSON Params:
        count (int, optional): The exact number of arguments required.
        names (list[str], optional): The exact list of argument names in order.
        exact_match (bool, optional): Used with `names`. If False, only checks
            for presence, not for exact list match. Defaults to True.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the constraint.

        Args:
            **kwargs: Keyword arguments from the JSON rule's constraint config.
                Can accept `count` (int), `names` (list[str]), and
                `exact_match` (bool).
        """
        self.expected_count: int | None = kwargs.get("count")
        self.expected_names: list[str] | None = kwargs.get("names")
        self.exact_match: bool = kwargs.get("exact_match", True)

    def check(self, nodes: list[ast.AST]) -> bool:
        """Checks if the function signature matches the criteria."""
        if not nodes:
            return True
        if not all(isinstance(node, ast.FunctionDef) for node in nodes):
            return False

        for node in nodes:
            actual_arg_names = [arg.arg for arg in node.args.args]
            if hasattr(node, "parent") and isinstance(node.parent, ast.ClassDef):
                if actual_arg_names:
                    actual_arg_names.pop(0)

            if not self._check_single_node(actual_arg_names):
                return False
        return True

    def _check_single_node(self, actual_arg_names: list[str]) -> bool:
        """Checks the argument list of a single function."""
        if self.expected_names is not None:
            if self.exact_match:
                return actual_arg_names == self.expected_names
            else:
                return set(self.expected_names).issubset(set(actual_arg_names))
        elif self.expected_count is not None:
            return len(actual_arg_names) == self.expected_count
        return False
