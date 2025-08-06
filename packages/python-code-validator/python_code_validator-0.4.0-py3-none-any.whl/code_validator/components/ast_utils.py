"""Provides utility functions for working with Python's Abstract Syntax Trees (AST).

This module contains helper functions that perform common operations on AST nodes,
such as enriching the tree with parent references. These utilities are used by
various components of the validator to simplify complex tree analysis.
"""

import ast


def enrich_ast_with_parents(tree: ast.Module) -> None:
    """Walks the AST and adds a 'parent' attribute to each node.

    This function mutates the AST in-place, making it easier to traverse upwards
    or determine the context of a specific node. This is a crucial preprocessing
    step for many complex validation rules.

    Args:
        tree: The root node of the AST (typically an ast.Module object) to enrich.
    """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node


def get_full_name(node: ast.AST) -> str | None:
    """A helper function to recursively build a full attribute name from an AST node.

    For example, for an `ast.Attribute` node representing `foo.bar.baz`, this
    function will return the string "foo.bar.baz".

    Args:
        node: The AST node to extract the name from.

    Returns:
        The full, dot-separated name as a string, or None if a name cannot be
        constructed.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = get_full_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None
