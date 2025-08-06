import ast
import unittest
from pathlib import Path

# Импортируем ВСЕ наши компоненты
from src.code_validator.rules_library.constraint_logic import (
    IsForbiddenConstraint,
    IsRequiredConstraint,
    MustBeTypeConstraint,
    MustInheritFromConstraint,
    NameMustBeInConstraint,
    ValueMustBeInConstraint,
)
from src.code_validator.rules_library.selector_nodes import (
    AssignmentSelector,
    ClassDefSelector,
    FunctionCallSelector,
    FunctionDefSelector,
    ImportStatementSelector,
    LiteralSelector,
)

# Загружаем наш тестовый код
FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_CODE_CONTENT = (FIXTURES_DIR / "valid_code.py").read_text(encoding="utf-8")
INVALID_CODE_CONTENT = (FIXTURES_DIR / "invalid_code.py").read_text(encoding="utf-8")

VALID_AST = ast.parse(VALID_CODE_CONTENT)
INVALID_AST = ast.parse(INVALID_CODE_CONTENT)


class TestFunctionDefSelector(unittest.TestCase):
    def test_finds_function(self):
        selector = FunctionDefSelector(name="main")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 1)
        node = nodes[0]
        self.assertIsInstance(node, ast.FunctionDef)
        self.assertEqual(node.name, "main")

    def test_finds_all_functions(self):
        selector = FunctionDefSelector(name="*")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 3)


class TestClassDefSelector(unittest.TestCase):
    def test_finds_class(self):
        selector = ClassDefSelector(name="MyTestClass")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "MyTestClass")


class TestImportStatementSelector(unittest.TestCase):
    def test_finds_import(self):
        selector = ImportStatementSelector(name="sys")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], ast.Import)

    def test_does_not_find_missing_import(self):
        selector = ImportStatementSelector(name="os")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 0)


class TestFunctionCallSelector(unittest.TestCase):
    def test_finds_function_call(self):
        selector = FunctionCallSelector(name="print")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].func.id, "print")

    def test_finds_forbidden_call(self):
        selector = FunctionCallSelector(name="eval")
        nodes = selector.select(INVALID_AST)
        self.assertEqual(len(nodes), 1)


class TestAssignmentSelector(unittest.TestCase):
    def test_finds_global_assignment(self):
        selector = AssignmentSelector(name="GLOBAL_CONSTANT")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], ast.Assign)

    def test_finds_attribute_assignment(self):
        # Этот тест требует `in_scope`, который мы еще не тестируем,
        # но мы можем проверить, что он находит присваивание в принципе
        selector = AssignmentSelector(name="self.value")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 1)


class TestLiteralSelector(unittest.TestCase):
    def test_finds_string_literals(self):
        selector = LiteralSelector(name="string")
        nodes = selector.select(VALID_AST)
        self.assertEqual(len(nodes), 6)  # 3 докстринга, 1 константа, 1 в print, 1 имя модуля __main__

    def test_finds_number_literal(self):
        selector = LiteralSelector(name="number")
        nodes = selector.select(INVALID_AST)
        # Находит 12345
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].value, 12345)


class TestIsRequiredAndForbidden(unittest.TestCase):
    def test_is_required(self):
        constraint = IsRequiredConstraint()
        self.assertTrue(constraint.check([ast.AST()]))
        self.assertFalse(constraint.check([]))

    def test_is_forbidden(self):
        constraint = IsForbiddenConstraint()
        self.assertFalse(constraint.check([ast.AST()]))
        self.assertTrue(constraint.check([]))


class TestMustInheritFrom(unittest.TestCase):
    def test_inheritance_passes(self):
        constraint = MustInheritFromConstraint(parent_name="MyParent")
        selector = ClassDefSelector(name="MyTestClass")
        nodes = selector.select(VALID_AST)
        self.assertTrue(constraint.check(nodes))

    def test_inheritance_fails(self):
        constraint = MustInheritFromConstraint(parent_name="WrongParent")
        selector = ClassDefSelector(name="MyTestClass")
        nodes = selector.select(VALID_AST)
        self.assertFalse(constraint.check(nodes))


class TestConstraints(unittest.TestCase):
    def test_is_required_and_forbidden(self):
        required = IsRequiredConstraint()
        forbidden = IsForbiddenConstraint()
        test_node = ast.Name(id="x", ctx=ast.Load())

        self.assertTrue(required.check([test_node]))
        self.assertFalse(required.check([]))
        self.assertFalse(forbidden.check([test_node]))
        self.assertTrue(forbidden.check([]))

    def test_must_inherit_from(self):
        constraint = MustInheritFromConstraint(parent_name="MyParent")
        selector = ClassDefSelector(name="MyTestClass")
        nodes = selector.select(VALID_AST)
        self.assertTrue(constraint.check(nodes))

    def test_must_be_type(self):
        constraint = MustBeTypeConstraint(expected_type="str")
        selector = AssignmentSelector(name="GLOBAL_CONSTANT")
        nodes = selector.select(VALID_AST)
        self.assertTrue(constraint.check(nodes))

    def test_name_must_be_in(self):
        # Создаем constraint
        constraint = NameMustBeInConstraint(allowed_names=["GLOBAL_CONSTANT", "MyParent"])

        # Тест, который должен пройти
        selector_ok = AssignmentSelector(name="GLOBAL_CONSTANT")
        nodes_ok = selector_ok.select(VALID_AST)
        self.assertTrue(constraint.check(nodes_ok), "Should pass for allowed name.")

        # Тест, который должен провалиться
        selector_fail = ClassDefSelector(name="MyTestClass")
        nodes_fail = selector_fail.select(VALID_AST)
        self.assertFalse(constraint.check(nodes_fail), "Should fail for not allowed name.")

    def test_value_must_be_in(self):
        constraint = ValueMustBeInConstraint(allowed_values=[10])

        # Создаем узлы для теста вручную
        node_ok = ast.Constant(value=10)
        node_fail = ast.Constant(value=99)

        self.assertTrue(constraint.check([node_ok]))
        self.assertFalse(constraint.check([node_fail]))


class TestAdvancedConstraints(unittest.TestCase):
    def setUp(self):
        self.empty_nodes = []
        self.one_node = [ast.Name(id="x")]

    def test_must_inherit_from_fails_on_no_parent_name(self):
        # Проверяем ветку `if not self.parent_name_to_find:`
        constraint = MustInheritFromConstraint(parent_name=None)
        self.assertFalse(constraint.check(self.one_node))

    def test_must_inherit_from_fails_on_wrong_node_count(self):
        # Проверяем ветку `if len(nodes) != 1:`
        constraint = MustInheritFromConstraint(parent_name="Parent")
        self.assertFalse(constraint.check(self.empty_nodes))
        self.assertFalse(constraint.check([ast.AST(), ast.AST()]))

    def test_must_be_type_handles_no_value(self):
        # Проверяем ветку `if value_node is None:`
        constraint = MustBeTypeConstraint(expected_type="int")
        # AnnAssign без значения: x: int
        node_without_value = ast.AnnAssign(target=ast.Name(id="x"), annotation=ast.Name(id="int"))
        self.assertTrue(constraint.check([node_without_value]))

    def test_value_must_be_in_with_empty_allowed_list(self):
        # Проверяем ветку `if not self.allowed_values:`
        constraint = ValueMustBeInConstraint(allowed_values=[])
        self.assertFalse(constraint.check([ast.Constant(value=5)]))
        self.assertTrue(constraint.check([]))


if __name__ == "__main__":
    unittest.main()
