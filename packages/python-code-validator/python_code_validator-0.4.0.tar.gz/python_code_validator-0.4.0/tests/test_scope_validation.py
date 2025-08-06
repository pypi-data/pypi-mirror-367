"""Tests for scope validation functionality."""

import json
import unittest
from pathlib import Path

from src.code_validator.config import AppConfig, LogLevel
from src.code_validator.core import StaticValidator
from src.code_validator.output import Console, setup_logging


class TestScopeValidation(unittest.TestCase):
    """Test scope validation with real arcade game example."""

    def setUp(self):
        """Set up test environment."""
        self.logger = setup_logging(LogLevel.CRITICAL)
        self.console = Console(self.logger, is_quiet=True)

    def test_hero_speed_attribute_missing(self):
        """Test that validation fails when Hero.__init__ is missing self.speed attribute."""
        # Code with intentional error: self.sped instead of self.speed
        test_code = '''
class Hero:
    def __init__(self):
        self.scale = 1.0
        self.sped = 300  # ERROR: should be self.speed
        self.health = 100

class Bullet:
    def __init__(self, speed=800):
        self.speed = speed  # This is correct but in wrong class
'''
        
        # Rule that should fail
        test_rules = {
            "validation_rules": [
                {
                    "rule_id": 16,
                    "message": "В конструкторе класса 'Hero' должен создаваться атрибут 'self.speed'.",
                    "check": {
                        "selector": {
                            "type": "assignment",
                            "name": "self.speed",
                            "in_scope": {
                                "class": "Hero",
                                "method": "__init__"
                            }
                        },
                        "constraint": {
                            "type": "is_required"
                        }
                    }
                }
            ]
        }
        
        # Create temporary files
        code_path = Path("temp_hero_test.py")
        rules_path = Path("temp_hero_rules.json")
        
        code_path.write_text(test_code, encoding="utf-8")
        rules_path.write_text(json.dumps(test_rules, indent=2), encoding="utf-8")
        
        try:
            config = AppConfig(
                solution_path=code_path,
                rules_path=rules_path,
                log_level=LogLevel.CRITICAL,
                is_quiet=True,
                exit_on_first_error=False,
            )
            
            validator = StaticValidator(config, self.console)
            result = validator.run()
            
            # Validation should FAIL because self.speed is not in Hero.__init__
            self.assertFalse(result, "Validation should fail when Hero.__init__ is missing self.speed")
            self.assertEqual(len(validator.failed_rules_id), 1, "Should have exactly 1 failed rule")
            self.assertEqual(validator.failed_rules_id[0].config.rule_id, 16, "Rule 16 should fail")
            
        finally:
            code_path.unlink(missing_ok=True)
            rules_path.unlink(missing_ok=True)

    def test_global_scope_assignment(self):
        """Test that global scope only finds assignments at module level."""
        test_code = '''
GLOBAL_VAR = 800  # This should be found

class Hero:
    def __init__(self):
        self.speed = 300  # This should NOT be found in global scope

def setup():
    local_var = 100  # This should NOT be found in global scope
'''
        
        test_rules = {
            "validation_rules": [
                {
                    "rule_id": 1,
                    "message": "Global variable GLOBAL_VAR is required.",
                    "check": {
                        "selector": {
                            "type": "assignment",
                            "name": "GLOBAL_VAR",
                            "in_scope": "global"
                        },
                        "constraint": {
                            "type": "is_required"
                        }
                    }
                },
                {
                    "rule_id": 2,
                    "message": "self.speed should not be found in global scope.",
                    "check": {
                        "selector": {
                            "type": "assignment",
                            "name": "self.speed",
                            "in_scope": "global"
                        },
                        "constraint": {
                            "type": "is_forbidden"
                        }
                    }
                },
                {
                    "rule_id": 3,
                    "message": "local_var should not be found in global scope.",
                    "check": {
                        "selector": {
                            "type": "assignment",
                            "name": "local_var",
                            "in_scope": "global"
                        },
                        "constraint": {
                            "type": "is_forbidden"
                        }
                    }
                }
            ]
        }
        
        code_path = Path("temp_global_test.py")
        rules_path = Path("temp_global_rules.json")
        
        code_path.write_text(test_code, encoding="utf-8")
        rules_path.write_text(json.dumps(test_rules, indent=2), encoding="utf-8")
        
        try:
            config = AppConfig(
                solution_path=code_path,
                rules_path=rules_path,
                log_level=LogLevel.CRITICAL,
                is_quiet=True,
                exit_on_first_error=False,
            )
            
            validator = StaticValidator(config, self.console)
            result = validator.run()
            
            # All rules should pass
            self.assertTrue(result, "All global scope rules should pass")
            self.assertEqual(len(validator.failed_rules_id), 0, "No rules should fail")
            
        finally:
            code_path.unlink(missing_ok=True)
            rules_path.unlink(missing_ok=True)

    def test_arcade_hero_game_validation(self):
        """Test validation of the real arcade hero game file."""
        config = AppConfig(
            solution_path=Path("tests/fixtures/arcade_hero_game.py"),
            rules_path=Path("tests/fixtures/r_advenced_arcade_.json"),
            log_level=LogLevel.CRITICAL,
            is_quiet=True,
            exit_on_first_error=False,
        )
        
        validator = StaticValidator(config, self.console)
        result = validator.run()
        
        # Validation should FAIL because of intentional errors in the code
        self.assertFalse(result, "Arcade hero game validation should fail due to intentional errors")
        
        # Check that specific rules fail
        failed_rule_ids = [rule.config.rule_id for rule in validator.failed_rules_id]
        
        # Rule 16: self.speed should be missing in Hero.__init__ (has self.sped instead)
        self.assertIn(16, failed_rule_ids, "Rule 16 should fail - Hero.__init__ missing self.speed")


if __name__ == "__main__":
    unittest.main()