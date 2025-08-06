"""Defines all data structures and configuration models for the validator.

This module contains Enum classes for standardized codes and several frozen
dataclasses that represent the structured configuration loaded from JSON files
and command-line arguments. These models ensure type safety and provide a
clear "shape" for the application's data.
"""

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any


class ExitCode(IntEnum):
    """Defines standardized exit codes for the command-line application."""

    SUCCESS = 0
    VALIDATION_FAILED = 1
    FILE_NOT_FOUND = 2
    JSON_ERROR = 3
    UNEXPECTED_ERROR = 10


class LogLevel(StrEnum):
    """Defines the supported logging levels for the application."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AppConfig:
    """Stores the main application configuration from CLI arguments.

    Attributes:
        solution_path: The file path to the Python solution to be validated.
        rules_path: The file path to the JSON rules file.
        log_level: The minimum logging level for console output.
        is_quiet: If True, suppresses all non-log output to stdout.
        exit_on_first_error: If True, halts validation after the first failed rule.
        max_messages: Maximum number of error messages to display. 0 for no limit. Default: 0.
    """

    solution_path: Path
    rules_path: Path
    log_level: LogLevel
    is_quiet: bool
    exit_on_first_error: bool
    max_messages: int = 0


@dataclass(frozen=True)
class SelectorConfig:
    """Represents the configuration for a Selector component from a JSON rule.

    This dataclass captures all possible keys within the "selector" block
    of a JSON validation rule.

    Attributes:
        type: The type of the selector to be used (e.g., "function_def").
        name: A generic name parameter used by many selectors (e.g., the name
            of a function, class, or module).
        node_type: The AST node type name for the `ast_node` selector.
        in_scope: The scope in which to apply the selector.
    """

    type: str
    name: str | None = None
    node_type: str | list[str] | None = None
    in_scope: str | dict[str, Any] | None = None


@dataclass(frozen=True)
class ConstraintConfig:
    """Represents the configuration for a Constraint component from a JSON rule.

    This dataclass captures all possible keys within the "constraint" block
    of a JSON validation rule.

    Attributes:
        type: The type of the constraint to be applied (e.g., "is_required").
        count: The exact number of nodes expected. Used by `is_required`.
        parent_name: The expected parent class name. Used by `must_inherit_from`.
        expected_type: The expected Python type name. Used by `must_be_type`.
        allowed_names: A list of permitted names. Used by `name_must_be_in`.
        allowed_values: A list of permitted literal values. Used by `value_must_be_in`.
        names: A list of expected argument names. Used by `must_have_args`.
        exact_match: A boolean flag for argument matching. Used by `must_have_args`.
    """

    type: str
    count: int | None = None
    parent_name: str | None = None
    expected_type: str | None = None
    allowed_names: list[str] | None = None
    allowed_values: list[Any] | None = None
    names: list[str] | None = None
    exact_match: bool | None = None


@dataclass(frozen=True)
class FullRuleCheck:
    """Represents the 'check' block within a full validation rule.

    Attributes:
        selector: The configuration for the selector component.
        constraint: The configuration for the constraint component.
    """

    selector: SelectorConfig
    constraint: ConstraintConfig


@dataclass(frozen=True)
class ShortRuleConfig:
    """Represents a 'short' (pre-defined) validation rule from JSON.

    Attributes:
        rule_id: The unique integer identifier for the rule.
        type: The string identifier for the short rule (e.g., "check_syntax").
        message: The error message to display if the rule fails.
        params: A dictionary of optional parameters for the rule.
    """

    rule_id: int
    type: str
    message: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FullRuleConfig:
    """Represents a 'full' (custom) validation rule with a selector and constraint.

    Attributes:
        rule_id: The unique integer identifier for the rule.
        message: The error message to display if the rule fails.
        check: An object containing the selector and constraint configurations.
        is_critical: If True, validation halts if this rule fails.
    """

    rule_id: int
    message: str
    check: FullRuleCheck
    is_critical: bool = False


# A type alias representing any possible rule configuration object.
ValidationRuleConfig = ShortRuleConfig | FullRuleConfig
