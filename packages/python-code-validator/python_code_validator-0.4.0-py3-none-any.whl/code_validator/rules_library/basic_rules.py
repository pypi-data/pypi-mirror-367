"""Contains concrete implementations of executable validation rules.

This module defines the handler classes for both "short" (pre-defined) and
"full" (custom selector/constraint) rules. Each class in this module implements
the `Rule` protocol from `definitions.py` and encapsulates the logic for a
specific type of validation check. The `RuleFactory` uses these classes to
instantiate the correct handler for each rule defined in a JSON file.
"""

import ast
import subprocess
import sys

from ..components.definitions import Constraint, Rule, Selector
from ..config import FullRuleConfig, ShortRuleConfig
from ..output import Console, LogLevel, log_initialization


class CheckSyntaxRule(Rule):
    """Handles the 'check_syntax' short rule.

    Note:
        The actual syntax validation is performed preemptively in the core
        validator engine when it calls `ast.parse()`. Therefore, this rule's
        `execute` method will only be called if the syntax is already valid.
        Its primary purpose is to exist so that a `check_syntax` rule can be
        formally defined in the JSON configuration.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, config: ShortRuleConfig, console: Console):
        """Initializes the syntax check rule handler.

        Args:
            config: The configuration object for this short rule.
            console: The console handler for output.
        """
        self.config = config
        self._console = console
        self.typo_suggestion: str | None = None

    def execute(self, tree: ast.Module | None, source_code: str | None = None) -> bool:
        """Confirms that syntax is valid.

        This method is guaranteed to be called only after a successful AST parsing.

        Returns:
            Always returns True.
        """
        self._console.print(f"Rule {self.config.rule_id}: Syntax is valid.", level=LogLevel.INFO)
        return True


class CheckLinterRule(Rule):
    """Handles the 'check_linter_pep8' short rule by running flake8.

    This rule executes the `flake8` linter as an external subprocess on the
    source code to check for style and common programming errors. It is
    configurable via the 'params' field in the JSON rule.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, config: ShortRuleConfig, console: Console):
        """Initializes a PEP8 linter check rule handler."""
        self.config = config
        self._console = console
        self.typo_suggestion: str | None = None

    def execute(self, tree: ast.Module | None, source_code: str | None = None) -> bool:
        """Executes the flake8 linter on the source code via a subprocess.

        It constructs a command-line call to `flake8`, passing the source code
        via stdin. This approach ensures isolation and uses flake8's stable
        CLI interface.

        Args:
            tree: Not used by this rule.
            source_code: The raw source code string to be linted.

        Returns:
            True if no PEP8 violations are found, False otherwise.
        """
        if not source_code:
            self._console.print("Source code is empty, skipping PEP8 check.", level=LogLevel.WARNING)
            return True

        self._console.print(f"Rule {self.config.rule_id}: Running PEP8 linter...", level=LogLevel.INFO)

        params = self.config.params
        args = [sys.executable, "-m", "flake8", "-"]

        if select_list := params.get("select"):
            args.append(f"--select={','.join(select_list)}")
        elif ignore_list := params.get("ignore"):
            args.append(f"--ignore={','.join(ignore_list)}")

        self._console.print(f"Arguments for flake8: {args}", level=LogLevel.TRACE)

        try:
            process = subprocess.run(
                args,
                input=source_code,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            if process.returncode != 0 and process.stdout:
                linter_output = process.stdout.strip()
                self._console.print(f"Flake8 found issues:\n{linter_output}", level=LogLevel.WARNING, show_user=True)
                return False
            elif process.returncode != 0:
                self._console.print(
                    f"Flake8 exited with code {process.returncode}:\n{process.stderr}", level=LogLevel.ERROR
                )
                return False

            self._console.print("PEP8 check passed.", level=LogLevel.INFO)
            return True
        except FileNotFoundError:
            self._console.print("flake8 not found. Is it installed in the venv?", level=LogLevel.CRITICAL)
            return False
        except Exception as e:
            self._console.print(f"An unexpected error occurred while running flake8: {e}", level=LogLevel.CRITICAL)
            return False


class FullRuleHandler(Rule):
    """Handles a full, custom rule composed of a selector and a constraint.

    This class acts as a generic executor for complex rules. It does not contain
    any specific validation logic itself but instead orchestrates the interaction
    between a Selector and a Constraint object.

    Attributes:
        config (FullRuleConfig): The dataclass object holding the rule's config.
        _selector (Selector): The selector object responsible for finding nodes.
        _constraint (Constraint): The constraint object for checking the nodes.
        _console (Console): The console handler for logging.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, config: FullRuleConfig, selector: Selector, constraint: Constraint, console: Console):
        """Initializes a full rule handler.

        Args:
            config: The configuration for the full rule.
            selector: An initialized Selector object.
            constraint: An initialized Constraint object.
            console: The console handler for logging.
        """
        self.config = config
        self._selector = selector
        self._constraint = constraint
        self._console = console
        self.typo_suggestion: str | None = None

    def execute(self, tree: ast.Module | None, source_code: str | None = None) -> bool:
        """Executes the rule by running the selector and applying the constraint.

        Args:
            tree: The enriched AST of the source code.
            source_code: Not used by this rule.

        Returns:
            The boolean result of applying the constraint to the selected nodes.
        """
        if not tree:
            self._console.print("AST not available, skipping rule.", level=LogLevel.WARNING)
            return True

        self._console.print(f"Applying selector: {self._selector.__class__.__name__}", level=LogLevel.TRACE)
        selected_nodes = self._selector.select(tree)

        self._console.print(f"Applying constraint: {self._constraint.__class__.__name__}", level=LogLevel.TRACE)

        # Check if constraint supports typo detection context
        if hasattr(self._constraint, "check_with_context"):
            # Get file path from console context if available
            file_path = getattr(self._console, "_current_file_path", "<unknown>")

            context_result = self._constraint.check_with_context(
                selected_nodes,
                target_name=self.config.check.selector.name,
                scope_config=self.config.check.selector.in_scope,
                ast_tree=tree,
                file_path=file_path,
                console=self._console,
            )

            # Handle both old (bool) and new (tuple) return formats
            if isinstance(context_result, tuple):
                result, typo_suggestion = context_result
                self.typo_suggestion = typo_suggestion
                return result
            else:
                # Old format - just boolean result
                return context_result
        else:
            return self._constraint.check(selected_nodes)
