"""Contains concrete implementations of all Selector components.

Each class in this module implements the `Selector` protocol and is responsible
for finding and returning specific types of nodes from an Abstract Syntax Tree.
They use `ast.walk` to traverse the tree and can be constrained to specific
scopes via the `ScopedSelector` base class, which uses the `scope_handler`.
These classes are instantiated by the `SelectorFactory`.
"""

import ast
from typing import Any

from ..components.ast_utils import get_full_name
from ..components.definitions import Selector
from ..components.scope_handler import find_scope_node
from ..output import LogLevel, log_initialization


class ScopedSelector(Selector):
    """An abstract base class for selectors that support scoping.

    This class provides a common mechanism for subclasses to narrow their search
    to a specific part of the AST (e.g., a single function or class) before
    performing their selection logic.

    Attributes:
        in_scope_config (dict | str | None): The configuration dictionary or
            string that defines the desired scope.
    """

    def __init__(self, **kwargs: Any):
        """Initializes the ScopedSelector base class.

        Args:
            **kwargs: Keyword arguments passed from a subclass constructor.
                It extracts the `in_scope` configuration.
        """
        self.in_scope_config = kwargs.get("in_scope")

    def _get_search_tree(self, tree: ast.Module) -> ast.AST | None:
        """Determines the root node for the search based on the scope config.

        If no scope is defined or if it's 'global', the whole tree is used.
        Otherwise, it uses `find_scope_node` to locate the specific subtree.

        Args:
            tree: The root of the full AST.

        Returns:
            The AST node to start the search from, or None if the scope
            could not be found.
        """
        if not self.in_scope_config or self.in_scope_config == "global":
            return tree

        scope_node = find_scope_node(tree, self.in_scope_config)
        return scope_node

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Abstract select method to be implemented by subclasses."""
        raise NotImplementedError


class FunctionDefSelector(ScopedSelector):
    """Selects function definition (`def`) nodes from an AST.

    JSON Params:
        name (str): The name of the function to find. Use "*" to find all.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the FunctionDefSelector.

        Args:
            **kwargs: Keyword arguments from the JSON rule's selector config.
                Expects `name` (str) and optionally `in_scope` (dict).
        """
        super().__init__(**kwargs)
        self.name_to_find = kwargs.get("name")

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all `ast.FunctionDef` nodes that match the name criteria."""
        search_tree = self._get_search_tree(tree)
        if not search_tree:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем только в tree.body, не рекурсивно
        if self.in_scope_config == "global":
            nodes_to_check = search_tree.body
        else:
            # Для других scope используем ast.walk как раньше
            nodes_to_check = ast.walk(search_tree)

        for node in nodes_to_check:
            if isinstance(node, ast.FunctionDef):
                if self.name_to_find == "*" or node.name == self.name_to_find:
                    found_nodes.append(node)
        return found_nodes


class ClassDefSelector(ScopedSelector):
    """Selects class definition (`class`) nodes from an AST.

    JSON Params:
        name (str): The name of the class to find. Use "*" to find all.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the selector."""
        super().__init__(**kwargs)
        self.name_to_find = kwargs.get("name")

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all `ast.ClassDef` nodes that match the name criteria."""
        search_tree = self._get_search_tree(tree)
        if not search_tree:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем только в tree.body, не рекурсивно
        if self.in_scope_config == "global":
            nodes_to_check = search_tree.body
        else:
            # Для других scope используем ast.walk как раньше
            nodes_to_check = ast.walk(search_tree)

        for node in nodes_to_check:
            if isinstance(node, ast.ClassDef):
                if self.name_to_find == "*" or node.name == self.name_to_find:
                    found_nodes.append(node)
        return found_nodes


class ImportStatementSelector(ScopedSelector):
    """Selects import nodes (`import` or `from...import`) from an AST.

    JSON Params:
        name (str): The name of the module to find (e.g., "os", "requests").
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the ImportStatementSelector.

        Args:
            **kwargs: Keyword arguments from the JSON rule's selector config.
                Expects `name` (str) for the module name and optionally `in_scope`.
        """
        super().__init__(**kwargs)
        self.module_name_to_find = kwargs.get("name")

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all import-related nodes that match the name criteria."""
        if not self.module_name_to_find:
            return []

        search_tree = self._get_search_tree(tree)
        if not search_tree:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем только в tree.body, не рекурсивно
        if self.in_scope_config == "global":
            nodes_to_check = search_tree.body
        else:
            # Для других scope используем ast.walk как раньше
            nodes_to_check = ast.walk(search_tree)

        for node in nodes_to_check:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Проверяем 'os' в 'import os.path'
                    module_parts = alias.name.split(".")
                    if alias.name.startswith(self.module_name_to_find) or self.module_name_to_find in module_parts:
                        found_nodes.append(node)
                        break
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(self.module_name_to_find):
                    found_nodes.append(node)

        return found_nodes


class FunctionCallSelector(ScopedSelector):
    """Selects function call nodes from an AST.

    This can find simple function calls (`my_func()`) and method calls
    (`requests.get()`).

    JSON Params:
        name (str): The full name of the function being called.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the selector."""
        super().__init__(**kwargs)
        self.name_to_find = kwargs.get("name")

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all `ast.Call` nodes that match the name criteria."""
        search_tree = self._get_search_tree(tree)
        if not search_tree:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем на уровне модуля, но включаем содержимое if __name__ == "__main__"
        if self.in_scope_config == "global":
            # Ищем в прямых детях модуля и в if __name__ == "__main__" блоках
            for node in search_tree.body:
                if isinstance(node, ast.Call):
                    full_name = get_full_name(node.func)
                    if full_name and full_name == self.name_to_find:
                        found_nodes.append(node)
                elif isinstance(node, ast.If):
                    # Проверяем, является ли это if __name__ == "__main__"
                    if self._is_main_guard(node):
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                full_name = get_full_name(child.func)
                                if full_name and full_name == self.name_to_find:
                                    found_nodes.append(child)
        else:
            # Для других scope используем ast.walk как раньше
            for node in ast.walk(search_tree):
                if isinstance(node, ast.Call):
                    full_name = get_full_name(node.func)
                    if full_name and full_name == self.name_to_find:
                        found_nodes.append(node)
        return found_nodes

    @staticmethod
    def _is_main_guard(node: ast.If) -> bool:
        """Check node, if is block __name__ == "__main__"."""
        if not isinstance(node.test, ast.Compare):
            return False

        left = node.test.left
        if not isinstance(left, ast.Name) or left.id != "__name__":
            return False

        if len(node.test.ops) != 1 or not isinstance(node.test.ops[0], ast.Eq):
            return False

        if len(node.test.comparators) != 1:
            return False

        comparator = node.test.comparators[0]
        return isinstance(comparator, ast.Constant) and comparator.value == "__main__"


class AssignmentSelector(ScopedSelector):
    """Selects assignment nodes (`=` or `:=` or type-annotated).

    This can find assignments to simple variables (`x = 5`) and attributes
    (`self.player = ...`).

    JSON Params:
        name (str): The full name of the variable or attribute being assigned to.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the AssignmentSelector.

        Args:
            **kwargs: Keyword arguments from the JSON rule's selector config.
                Expects `name` (str) for the assignment target and optionally `in_scope`.
        """
        super().__init__(**kwargs)
        self.target_name_to_find = kwargs.get("name")

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all `ast.Assign` or `ast.AnnAssign` nodes matching the target name."""
        search_tree = self._get_search_tree(tree)
        if not search_tree:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем только в tree.body, не рекурсивно
        if self.in_scope_config == "global":
            nodes_to_check = search_tree.body
        else:
            # Для других scope используем ast.walk как раньше
            nodes_to_check = ast.walk(search_tree)

        for node in nodes_to_check:
            # Мы поддерживаем и простое присваивание (x=5), и с аннотацией (x: int = 5)
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                # Целей присваивания может быть несколько (a = b = 5)
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    full_name = get_full_name(target)
                    if full_name and (self.target_name_to_find == "*" or full_name == self.target_name_to_find):
                        found_nodes.append(node)
        return found_nodes


class UsageSelector(ScopedSelector):
    """Selects nodes where a variable or attribute is used (read).

    This finds nodes in a "load" context, meaning the value of the variable
    is being accessed, not assigned.

    JSON Params:
        name (str): The name of the variable or attribute being used.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the UsageSelector.

        Args:
            **kwargs: Keyword arguments from the JSON rule's selector config.
                Expects `name` (str) for the variable/attribute being used and
                optionally `in_scope`.
        """
        super().__init__(**kwargs)
        self.variable_name_to_find = kwargs.get("name")

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all `ast.Name` nodes (in load context) matching the name."""
        search_tree = self._get_search_tree(tree)
        if not search_tree:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем только в tree.body, не рекурсивно
        if self.in_scope_config == "global":
            nodes_to_check = search_tree.body
        else:
            # Для других scope используем ast.walk как раньше
            nodes_to_check = ast.walk(search_tree)

        for node in nodes_to_check:
            # Проверяем и простые имена, и атрибуты, когда их "читают"
            if isinstance(node, (ast.Name, ast.Attribute)) and isinstance(getattr(node, "ctx", None), ast.Load):
                full_name = get_full_name(node)
                if full_name and full_name == self.variable_name_to_find:
                    found_nodes.append(node)
        return found_nodes


class LiteralSelector(ScopedSelector):
    """Selects literal nodes (e.g., numbers, strings), ignoring docstrings.

    JSON Params:
        name (str): The type of literal to find. Supported: "number", "string".
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the LiteralSelector.

        Args:
            **kwargs: Keyword arguments from the JSON rule's selector config.
                Expects `name` (str) to be "string" or "number" and optionally
                `in_scope`.
        """
        super().__init__(**kwargs)
        self.literal_type = kwargs.get("name")

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all ast.Constant nodes that match the type criteria.

        This method traverses the given AST (or a sub-tree defined by `in_scope`)
        and collects all number or string literals. It contains special logic
        to intelligently ignore nodes that are likely to be docstrings or parts
        of f-strings to avoid false positives.

        Args:
            tree: The root of the AST (the module object) to be searched.

        Returns:
            A list of `ast.Constant` nodes matching the criteria.
        """
        search_tree = self._get_search_tree(tree)
        if not search_tree:
            return []

        type_map = {"number": (int, float), "string": (str,)}
        expected_py_types = type_map.get(self.literal_type)
        if not expected_py_types:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем только в tree.body, не рекурсивно
        if self.in_scope_config == "global":
            nodes_to_check = search_tree.body
        else:
            # Для других scope используем ast.walk как раньше
            nodes_to_check = ast.walk(search_tree)

        for node in nodes_to_check:
            # Мы ищем только узлы Constant
            if not isinstance(node, ast.Constant):
                continue

            # Проверяем тип значения внутри константы
            if not isinstance(node.value, expected_py_types):
                continue

            # Пропускаем докстринги
            if hasattr(node, "parent") and isinstance(node.parent, ast.Expr):
                continue

            # Пропускаем f-строки
            if hasattr(node, "parent") and isinstance(node.parent, ast.JoinedStr):
                continue

            found_nodes.append(node)

        return found_nodes


class AstNodeSelector(ScopedSelector):
    """A generic selector for finding any AST node by its class name.

    This is a powerful, low-level selector for advanced use cases.

    JSON Params:
        node_type (str | list[str]): The name(s) of the AST node types to find,
            as defined in the `ast` module (e.g., "For", "While", "Try").
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, **kwargs: Any):
        """Initializes the AstNodeSelector.

        Args:
            **kwargs: Keyword arguments from the JSON rule's selector config.
                Expects `node_type` (str or list[str]) and optionally `in_scope`.
        """
        super().__init__(**kwargs)
        node_type_arg = kwargs.get("node_type")

        # Поддерживаем и одну строку, и список строк
        if isinstance(node_type_arg, list):
            self.node_types_to_find = tuple(getattr(ast, nt) for nt in node_type_arg if hasattr(ast, nt))
        elif isinstance(node_type_arg, str) and hasattr(ast, node_type_arg):
            self.node_types_to_find = (getattr(ast, node_type_arg),)
        else:
            self.node_types_to_find = ()

    def select(self, tree: ast.Module) -> list[ast.AST]:
        """Finds all AST nodes that are instances of the specified types."""
        search_tree = self._get_search_tree(tree)
        if not search_tree or not self.node_types_to_find:
            return []

        found_nodes: list[ast.AST] = []

        # Для глобального scope ищем только в tree.body, не рекурсивно
        if self.in_scope_config == "global":
            nodes_to_check = search_tree.body
        else:
            # Для других scope используем ast.walk как раньше
            nodes_to_check = ast.walk(search_tree)

        for node in nodes_to_check:
            if isinstance(node, self.node_types_to_find):
                found_nodes.append(node)
        return found_nodes
