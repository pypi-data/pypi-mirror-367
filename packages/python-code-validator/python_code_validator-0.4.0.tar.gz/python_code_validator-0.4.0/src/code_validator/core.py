"""The core engine of the Python Code Validator.

This module contains the main orchestrator class, `StaticValidator`, which is
responsible for managing the entire validation lifecycle. It loads the source
code and a set of JSON rules, then uses a factory-based component system to
execute each rule and report the results.

The core is designed to be decoupled from the specific implementations of rules,
selectors, and constraints, allowing for high extensibility.

Example:
    To run a validation, you would typically use the CLI, but the core can also
    be used programmatically:

    .. code-block:: python

        from code_validator import StaticValidator, AppConfig, LogLevel
        from code_validator.output import Console, setup_logging
        from pathlib import Path
        import logging

        logger = logging.getLogger(__name__)
        console = Console(logger)
        config = AppConfig(
            solution_path=Path("path/to/solution.py"),
            rules_path=Path("path/to/rules.json"),
            log_level=LogLevel.INFO,
            is_silent=False,
            stop_on_first_fail=False
        )

        validator = StaticValidator(config, console)
        is_valid = validator.run()

        if is_valid:
            print("Validation Passed!")
        else:
            print(f"Validation Failed. Errors in: {validator.failed_rules_id}")

"""

import ast
import json

from .components.ast_utils import enrich_ast_with_parents
from .components.definitions import Rule
from .components.factories import RuleFactory
from .config import AppConfig, LogLevel, ShortRuleConfig
from .exceptions import RuleParsingError
from .output import Console, log_initialization


class StaticValidator:
    """Orchestrates the static validation process.

    This class is the main entry point for running a validation session. It
    manages loading of source files and rules, parsing the code into an AST,
    and iterating through the rules to execute them.

    Attributes:
        _config (AppConfig): The application configuration object.
        _console (Console): The handler for all logging and stdout printing.
        _rule_factory (RuleFactory): The factory responsible for creating rule objects.
        _source_code (str): The raw text content of the Python file being validated.
        _ast_tree (ast.Module | None): The Abstract Syntax Tree of the source code.
        _rules (list[Rule]): A list of initialized, executable rule objects.
        _failed_rules (list[Rule]): A list of rules that contained IDs of failed checks during the run.
    """

    @log_initialization(level=LogLevel.DEBUG)
    def __init__(self, config: AppConfig, console: Console):
        """Initializes the StaticValidator.

        Args:
            config: An `AppConfig` object containing all necessary run
                configurations, such as file paths and flags.
            console: A `Console` object for handling all output.
        """
        self._config = config
        self._console = console

        self._rule_factory = RuleFactory(self._console)
        self._source_code: str = ""
        self._ast_tree: ast.Module | None = None
        self._rules: list[Rule] = []
        self._failed_rules: list[Rule] = []

    @property
    def failed_rules_id(self) -> list[Rule]:
        """list[int]: A list of rule IDs that failed during the last run."""
        return self._failed_rules

    def _load_source_code(self) -> None:
        """Loads the content of the student's solution file into memory.

        Raises:
            FileNotFoundError: If the source file specified in the config does not exist.
            RuleParsingError: If the source file cannot be read for any other reason.
        """
        self._console.print(f"Reading source file: {self._config.solution_path}", level=LogLevel.DEBUG)
        try:
            self._source_code = self._config.solution_path.read_text(encoding="utf-8")
            self._console.print(f"Source code:\n{self._source_code}\n", level=LogLevel.TRACE)
        except FileNotFoundError:
            self._console.print("During reading source file raised FileNotFound", level=LogLevel.TRACE)
            raise
        except Exception as e:
            self._console.print("During reading source file raised some exception..", level=LogLevel.TRACE)
            raise RuleParsingError(f"Cannot read source file: {e}") from e

    def _load_and_parse_rules(self) -> None:
        """Loads and parses the JSON file into executable Rule objects.

        This method reads the JSON rules file, validates its basic structure,
        and then uses the `RuleFactory` to instantiate a list of concrete
        Rule objects.

        Raises:
            FileNotFoundError: If the rules file does not exist.
            RuleParsingError: If the JSON is malformed or a rule configuration
                is invalid.
        """
        self._console.print(f"Loading rules from: {self._config.rules_path}", level=LogLevel.DEBUG)
        try:
            rules_data = json.loads(self._config.rules_path.read_text(encoding="utf-8"))
            self._console.print(f"Load rules:\n{rules_data}", level=LogLevel.TRACE)
            raw_rules = rules_data.get("validation_rules")
            if not isinstance(raw_rules, list):
                raise RuleParsingError("`validation_rules` key not found or is not a list.")

            self._console.print(f"Found {len(raw_rules)}.", level=LogLevel.DEBUG)
            self._rules = [self._rule_factory.create(rule) for rule in raw_rules]
            self._console.print(f"Successfully parsed {len(self._rules)} rules.", level=LogLevel.DEBUG)
        except json.JSONDecodeError as e:
            self._console.print("During reading file of rules raised JsonDecodeError..", level=LogLevel.TRACE)
            raise RuleParsingError(f"Invalid JSON in rules file: {e}") from e
        except FileNotFoundError:
            self._console.print("During reading file of rules raised FileNotFound", level=LogLevel.TRACE)
            raise

    def _parse_ast_tree(self) -> bool:
        """Parses the loaded source code into an AST and enriches it.

        This method attempts to parse the source code. If successful, it calls
        a helper to add parent references to each node in the tree, which is
        crucial for many advanced checks. If a `SyntaxError` occurs, it
        checks if a `check_syntax` rule was defined to provide a custom message.

        Returns:
            bool: True if parsing was successful, False otherwise.
        """
        self._console.print("Parsing Abstract Syntax Tree (AST)...", level=LogLevel.DEBUG)
        try:
            self._console.print("Start parse source code.", level=LogLevel.TRACE)
            self._ast_tree = ast.parse(self._source_code)
            enrich_ast_with_parents(self._ast_tree)
            return True
        except SyntaxError as e:
            self._console.print("In source code SyntaxError..", level=LogLevel.TRACE)
            for rule in self._rules:
                if getattr(rule.config, "type", None) == "check_syntax":
                    self._console.print(rule.config.message, level=LogLevel.ERROR, show_user=True)
                    self._console.print(f"Failed rule id: {rule.config.rule_id}", level=LogLevel.DEBUG)
                    self._failed_rules.append(rule)
                    return False
            self._console.print(f"Syntax Error found: {e}", level=LogLevel.ERROR)
            return False

    def _report_errors(self) -> None:
        """Formats and prints collected validation errors to the console.

        This method is responsible for presenting the final list of failed
        rules to the user. It respects the `--max-messages` configuration
        to avoid cluttering the terminal. If the number of found errors
        exceeds the specified limit, it truncates the output and displays
        a summary message indicating how many more errors were found.

        The method retrieves the list of failed rules from `self._failed_rules`
        and the display limit from `self._config`. All user-facing output is
        channeled through the `self._console` object.

        Enhanced with numbered error messages and typo suggestions for better UX.

        It performs the following steps:
          1. Checks if any errors were recorded. If not, it returns immediately.
          2. Determines the subset of errors to display based on the configured
             `max_messages` limit (a value of 0 means no limit).
          3. Iterates through the selected error rules and prints their
             numbered failure messages with typo suggestions if available.
          4. If the error list was truncated, prints a summary line, e.g.,
             "... (5 more errors found)".
        """
        max_errors = self._config.max_messages
        num_errors = len(self._failed_rules)

        if num_errors == 0:
            return None

        errors_to_show = self._failed_rules
        if 0 < max_errors < num_errors:
            errors_to_show = self._failed_rules[:max_errors]

        for i, rule in enumerate(errors_to_show, 1):
            # Print numbered error message
            self._console.print(f"{i}. {rule.config.message}", level=LogLevel.WARNING, show_user=True)

            # Print typo suggestion if available
            if hasattr(rule, "typo_suggestion") and rule.typo_suggestion:
                # Add 4-space indentation to each line of the suggestion
                suggestion_lines = rule.typo_suggestion.split("\n")
                for line in suggestion_lines:
                    self._console.print(f"    {line}", level=LogLevel.WARNING, show_user=True)

                # Add empty line after suggestion for better readability
                if i < len(errors_to_show):  # Don't add empty line after last error
                    self._console.print("", level=LogLevel.WARNING, show_user=True)

        if 0 < max_errors < num_errors:
            remaining_count = num_errors - max_errors
            self._console.print(
                f"... ({remaining_count} more error{'s' if remaining_count > 1 else ''} found)",
                level=LogLevel.WARNING,
                show_user=True,
            )

    def run(self) -> bool:
        """Runs the entire validation process from start to finish.

        This is the main public method of the class. It orchestrates the
        sequence of loading, parsing, and rule execution.

        Returns:
            bool: True if all validation rules passed, False otherwise.

        Raises:
            RuleParsingError: Propagated from loading/parsing steps.
            FileNotFoundError: Propagated from loading steps.
        """
        try:
            self._load_source_code()
            self._load_and_parse_rules()

            if not self._parse_ast_tree():
                self._report_errors()
                return False

            self._console.print("Lead source code, load and parse rules and parsing code - PASS", level=LogLevel.DEBUG)

        except (FileNotFoundError, RuleParsingError) as e:
            self._console.print(
                f"In method `run` of 'StaticValidator' raised exception {e.__class__.__name__}", level=LogLevel.WARNING
            )
            raise

        # Set current file path for typo detection context
        self._console.set_current_file_path(str(self._config.solution_path))

        self._console.print("Starting check rules..", level=LogLevel.DEBUG)
        for rule in self._rules:
            if getattr(rule.config, "type", None) == "check_syntax":
                continue

            self._console.print(
                f"Executing rule: {rule.config.rule_id}"
                + (
                    f" [{rule.config.check.selector.type}, {rule.config.check.constraint.type}, "
                    f"is_critical={rule.config.is_critical}]"
                    if not isinstance(rule.config, ShortRuleConfig)
                    else ""
                ),
                level=LogLevel.INFO,
            )
            is_passed = rule.execute(self._ast_tree, self._source_code)
            if not is_passed:
                self._failed_rules.append(rule)
                # self._console.print(rule.config.message, level=LogLevel.WARNING, show_user=True)
                self._console.print(f"Rule {rule.config.rule_id} - FAIL", level=LogLevel.INFO)
                if getattr(rule.config, "is_critical", False):
                    self._console.print("Critical rule failed. Halting validation.", level=LogLevel.WARNING)
                    break
                elif self._config.exit_on_first_error:
                    self._console.print("Exiting on first error.", level=LogLevel.INFO)
                    break
            else:
                self._console.print(f"Rule {rule.config.rule_id} - PASS", level=LogLevel.INFO)

        self._report_errors()

        return not self._failed_rules
