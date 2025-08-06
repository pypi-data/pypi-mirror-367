import json
import unittest
from pathlib import Path

from src.code_validator.config import AppConfig, LogLevel
from src.code_validator.core import StaticValidator
from src.code_validator.exceptions import RuleParsingError
from src.code_validator.output import Console, setup_logging

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestStaticValidatorIntegration(unittest.TestCase):
    """Integration tests for the StaticValidator using fixture files."""

    def setUp(self):
        self.logger = setup_logging(LogLevel.CRITICAL)
        self.console = Console(self.logger, is_quiet=True)

    def run_validator(self, solution_file: str, rules_file: str) -> bool:
        """Helper function to run the validator with specific files."""
        config = AppConfig(
            solution_path=FIXTURES_DIR / solution_file,
            rules_path=FIXTURES_DIR / rules_file,
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=False,
        )
        validator = StaticValidator(config, self.console)
        return validator.run()

    def test_simple_program_passes_require_structure(self):
        """A valid program should pass basic structural checks."""
        result = self.run_validator("p01_simple_program.py", "r01_require_structure.json")
        self.assertTrue(result)

    def test_invalid_program_fails_require_structure(self):
        """An invalid program should fail basic structural checks."""
        result = self.run_validator("p02_forbidden_constructs.py", "r01_require_structure.json")
        self.assertFalse(result)

    def test_program_with_forbidden_constructs_fails(self):
        """A program with forbidden elements should fail the corresponding checks."""
        result = self.run_validator("p02_forbidden_constructs.py", "r02_forbid_constructs.json")
        self.assertFalse(result)

    def test_simple_program_passes_forbid_constructs(self):
        """A clean program should pass the forbidden checks."""
        result = self.run_validator("p01_simple_program.py", "r02_forbid_constructs.json")
        self.assertTrue(result)

    def test_oop_program_passes_oop_checks(self):
        """A correct OOP program should pass OOP-related checks."""
        result = self.run_validator("p03_oop_structure.py", "r03_check_oop.json")
        self.assertTrue(result)

    def test_wrong_oop_program_fails_oop_checks(self):
        """An incorrect OOP program should fail OOP-related checks."""
        result = self.run_validator("p02_forbidden_constructs.py", "r03_check_oop.json")
        self.assertFalse(result)

    def test_magic_numbers_fail_check(self):
        """A program with magic numbers should fail the check."""
        result = self.run_validator("p04_magic_numbers.py", "r04_forbid_magic_numbers.json")
        self.assertFalse(result)

    def test_run_with_malformed_rule_raises_error(self):
        """Tests that a malformed JSON rule raises RuleParsingError."""
        # Создаем JSON с ошибкой: нет ключа 'type' или 'check'
        malformed_rules = {
            "description": "Malformed rules",
            "validation_rules": [{"rule_id": 999, "message": "This rule is broken"}],
        }
        rules_path = FIXTURES_DIR / "temp_malformed_rules.json"
        with open(rules_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(malformed_rules, f)

        config = AppConfig(
            solution_path=FIXTURES_DIR / "valid_code.py",
            rules_path=rules_path,
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=False,
        )
        validator = StaticValidator(config, self.console)

        # Проверяем, что вызов .run() вызывает именно наше исключение
        with self.assertRaises(RuleParsingError):
            validator.run()

        rules_path.unlink()

    def test_linter_rule_passes_for_valid_code(self):
        """Tests that CheckLinterRule passes for clean code."""
        rules = {
            "validation_rules": [
                {
                    "rule_id": 1,
                    "type": "check_linter_pep8",
                    "message": "PEP8 fail",
                    "params": {"ignore": ["F401", "E302", "E305", "E261"]},
                }
            ]
        }
        rules_path = FIXTURES_DIR / "temp_linter_rules.json"
        with open(rules_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(rules, f)

        result = self.run_validator("p01_simple_program.py", str(rules_path))
        rules_path.unlink()
        self.assertTrue(result)

    def test_linter_rule_fails_for_invalid_code(self):
        """Tests that CheckLinterRule fails for messy code."""
        rules = {
            "validation_rules": [
                {
                    "rule_id": 1,
                    "type": "check_linter_pep8",
                    "message": "PEP8 fail",
                }
            ]
        }
        rules_path = FIXTURES_DIR / "temp_linter_rules_fail.json"
        with open(rules_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(rules, f)

        result = self.run_validator("p02_forbidden_constructs.py", str(rules_path))
        rules_path.unlink()

        self.assertFalse(result)

    def test_exit_on_first_error_works(self):
        """Tests that the validator stops after the first failure if flag is set."""
        rules = {
            "validation_rules": [
                {
                    "rule_id": 1,
                    "message": "fail 1",
                    "check": {
                        "selector": {"type": "import_statement", "name": "os"},
                        "constraint": {"type": "is_required"},  # Это провалится
                    },
                },
                {
                    "rule_id": 2,
                    "message": "fail 2",
                    "check": {
                        "selector": {"type": "function_def", "name": "non_existent"},
                        "constraint": {"type": "is_required"},  # Это тоже провалится
                    },
                },
            ]
        }
        rules_path = FIXTURES_DIR / "temp_stop_rules.json"
        with open(rules_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(rules, f)

        config = AppConfig(
            solution_path=FIXTURES_DIR / "p01_simple_program.py",
            rules_path=rules_path,
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=True,
        )
        validator = StaticValidator(config, self.console)
        validator.run()
        rules_path.unlink()

        # Проверяем, что провалилось только одно правило, а не два
        self.assertEqual(len(validator.failed_rules_id), 1)
        # noinspection PyTypeChecker
        self.assertEqual(validator.failed_rules_id[0].config.rule_id, 1)

    def test_unknown_rule_type_raises_error(self):
        """Tests that an unknown rule type in JSON raises RuleParsingError."""
        rules = {"validation_rules": [{"rule_id": 99, "type": "non_existent_check"}]}
        rules_path = FIXTURES_DIR / "temp_unknown_rules.json"
        with open(rules_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(rules, f)

        with self.assertRaises(RuleParsingError):
            self.run_validator("p01_simple_program.py", str(rules_path))

        rules_path.unlink()

    def test_empty_rules_list_raises_error(self):
        rules = {}
        rules_path = FIXTURES_DIR / "temp_unknown_rules.json"
        with open(rules_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(rules, f)

        with self.assertRaises(RuleParsingError):
            self.run_validator("p01_simple_program.py", str(rules_path))

        rules_path.unlink()

    def test_syntax_error_python_code(self):
        good_result = self.run_validator("invalid_syntax.ppy", "r06_api_rules.json")
        self.assertFalse(good_result, "A invalid code should fail validation.")

        good_result = self.run_validator("invalid_syntax.ppy", "basic_rules.json")
        self.assertFalse(good_result, "A invalid code should fail validation.")

    def test_api_client_validation(self):
        """Tests validation rules specific to an API client task."""
        # Хороший код должен пройти
        good_result = self.run_validator("p06_api_client.py", "r06_api_rules.json")
        self.assertTrue(good_result, "A valid API client should pass a_api_rules.")

        # Плохой код должен провалиться
        bad_result = self.run_validator("p07_bad_api_client.py", "r06_api_rules.json")
        self.assertFalse(bad_result, "A bad API client should fail api_rules.")

    def test_full_rule_sets(self):
        """Runs all comprehensive rule sets against their corresponding code files."""
        test_cases = [
            # Название теста, файл с кодом, файл с правилами, ожидаемый результат (True=pass)
            ("debug_pep8_valid", "p01_simple_program.py", "debug_pep8.json", True),
            ("py_general_valid", "p01_simple_program.py", "r_full_py_general.json", True),
            ("api_valid", "p06_api_client.py", "r_full_api_rules.json", True),
            ("flask_valid", "p08_flask_app.py", "r_full_flask_rules.json", True),
            ("arcade_valid", "p09_arcade_app.py", "r_full_arcade_rules.json", True),
        ]

        for name, code_file, rules_file, expected_result in test_cases:
            with self.subTest(name=name):
                # Пропускаем тесты, для которых еще нет реализации
                if "flask" in name or "arcade" in name:
                    self.skipTest(f"Skipping {name}: advanced selectors not implemented yet.")

                result = self.run_validator(code_file, rules_file)
                if expected_result:
                    self.assertTrue(result, f"Test case '{name}' should pass.")
                else:
                    self.assertFalse(result, f"Test case '{name}' should fail.")


class TestValidatorRobustness(unittest.TestCase):
    """Tests the validator's robustness against bad inputs and edge cases."""

    def setUp(self):
        self.logger = setup_logging(LogLevel.CRITICAL)
        self.console = Console(self.logger, is_quiet=True)
        self.valid_rules_path = FIXTURES_DIR / "r01_require_structure.json"

    def run_validator(self, solution_file: str, rules_file: str) -> bool:
        """Helper function to run the validator with specific files."""
        config = AppConfig(
            solution_path=FIXTURES_DIR / solution_file,
            rules_path=FIXTURES_DIR / rules_file,
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=False,
        )
        validator = StaticValidator(config, self.console)
        return validator.run()

    def run_validator_config(self, config: AppConfig) -> bool:
        """Helper to run validator with a pre-made config."""
        validator = StaticValidator(config, self.console)
        return validator.run()

    def test_handles_empty_solution_file(self):
        """Tests that validator handles an empty source file gracefully."""
        config = AppConfig(
            solution_path=FIXTURES_DIR / "empty.py",
            rules_path=self.valid_rules_path,
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=False,
        )
        # Ожидаем, что проверка провалится (т.к. в пустом файле нет нужных функций),
        # но сама программа не упадет с ошибкой.
        result = self.run_validator_config(config)
        self.assertFalse(result)

    def test_raises_error_for_non_existent_solution_file(self):
        """Tests that a specific error is raised for a missing solution file."""
        config = AppConfig(
            solution_path=FIXTURES_DIR / "non_existent_file.py",
            rules_path=self.valid_rules_path,
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=False,
        )
        # Проверяем, что вызов .run() вызывает именно FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            validator = StaticValidator(config, self.console)
            validator.run()  # Этот вызов должен упасть

    def test_raises_error_for_malformed_json(self):
        """Tests that a specific error is raised for a broken JSON rules file."""
        config = AppConfig(
            solution_path=FIXTURES_DIR / "valid_code.py",
            rules_path=FIXTURES_DIR / "malformed.json",
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=False,
        )
        with self.assertRaises(RuleParsingError):
            validator = StaticValidator(config, self.console)
            validator.run()

    def test_api_validation_on_flask_code_fails(self):
        """Cross-check: API rules should fail on Flask code."""
        result = self.run_validator("p08_flask_app.py", "r06_api_rules.json")
        self.assertFalse(result, "Flask code should not pass API rules (e.g., missing 'requests' import).")

    def test_arcade_validation_on_arcade_code_passes(self):
        """Tests that Arcade code passes a simple Arcade-specific rule."""
        arcade_rules = {
            "validation_rules": [
                {
                    "rule_id": 901,
                    "message": "Main class must inherit from arcade.Window",
                    "check": {
                        "selector": {"type": "class_def", "name": "MyArcadeGame"},
                        "constraint": {"type": "must_inherit_from", "parent_name": "arcade.Window"},
                    },
                }
            ]
        }
        rules_path = FIXTURES_DIR / "temp_arcade_rules.json"
        with open(rules_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(arcade_rules, f)

        result = self.run_validator("p09_arcade_app.py", str(rules_path))
        rules_path.unlink()
        self.assertTrue(result)
