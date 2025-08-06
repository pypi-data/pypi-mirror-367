import ast
import unittest
from pathlib import Path

from src.code_validator.components.scope_handler import find_scope_node

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ADVANCED_CODE = (FIXTURES_DIR / "p05_advanced_code.py").read_text(encoding="utf-8")
ADVANCED_AST = ast.parse(ADVANCED_CODE)


class TestScopeHandler(unittest.TestCase):
    def test_find_global_function(self):
        scope_config = {"function": "top_level_func"}
        node = find_scope_node(ADVANCED_AST, scope_config)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, ast.FunctionDef)
        self.assertEqual(node.name, "top_level_func")

    def test_find_class(self):
        scope_config = {"class": "MyAdvancedClass"}
        node = find_scope_node(ADVANCED_AST, scope_config)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, ast.ClassDef)

    def test_find_method_in_class(self):
        scope_config = {"class": "MyAdvancedClass", "method": "method_a"}
        node = find_scope_node(ADVANCED_AST, scope_config)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, ast.FunctionDef)
        self.assertEqual(node.name, "method_a")

    def test_returns_none_for_missing_scope(self):
        scope_config = {"function": "non_existent"}
        node = find_scope_node(ADVANCED_AST, scope_config)
        self.assertIsNone(node)

    def test_returns_none_for_missing_method(self):
        scope_config = {"class": "MyAdvancedClass", "method": "non_existent_method"}
        node = find_scope_node(ADVANCED_AST, scope_config)
        self.assertIsNone(node)
