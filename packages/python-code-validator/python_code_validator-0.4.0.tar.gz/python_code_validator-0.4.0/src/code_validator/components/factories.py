"""Contains factories for creating rule, selector, and constraint objects.

This module implements the Factory Method design pattern to decouple the core
validator engine from the concrete implementations of its components. Factories
are responsible for parsing raw dictionary configurations from the main JSON
rules file and instantiating the appropriate handler classes from the
`rules_library`.
"""

import dataclasses
from typing import Any, Type, TypeVar

from ..config import ConstraintConfig, FullRuleCheck, FullRuleConfig, LogLevel, SelectorConfig, ShortRuleConfig
from ..exceptions import RuleParsingError
from ..output import Console, log_initialization
from ..rules_library.basic_rules import CheckLinterRule, CheckSyntaxRule, FullRuleHandler
from ..rules_library.constraint_logic import (
    IsForbiddenConstraint,
    IsRequiredConstraint,
    MustBeTypeConstraint,
    MustHaveArgsConstraint,
    MustInheritFromConstraint,
    NameMustBeInConstraint,
    ValueMustBeInConstraint,
)
from ..rules_library.selector_nodes import (
    AssignmentSelector,
    AstNodeSelector,
    ClassDefSelector,
    FunctionCallSelector,
    FunctionDefSelector,
    ImportStatementSelector,
    LiteralSelector,
    UsageSelector,
)
from .definitions import Constraint, Rule, Selector

T = TypeVar("T")


def _create_dataclass_from_dict(cls: Type[T], data: dict[str, Any]) -> T:
    """Safely creates a dataclass instance from a dictionary.

    This helper function filters the input dictionary to include only the keys
    that correspond to fields in the target dataclass, preventing `TypeError`
    for unexpected arguments.

    Args:
        cls: The dataclass type to instantiate.
        data: The dictionary with raw data.

    Returns:
        An instance of the specified dataclass.
    """
    expected_fields = {f.name for f in dataclasses.fields(cls)}
    filtered_data = {k: v for k, v in data.items() if k in expected_fields}
    return cls(**filtered_data)


class RuleFactory:
    """Creates rule handler objects from raw dictionary configuration.

    This is the main factory that acts as an entry point for parsing the
    'validation_rules' list from a JSON file. It determines whether a rule is
    a "short" pre-defined type or a "full" custom rule and delegates the
    creation of its components to other specialized factories.

    Attributes:
        _console (Console): An instance of the console for logging.
        _selector_factory (SelectorFactory): A factory for creating selector objects.
        _constraint_factory (ConstraintFactory): A factory for creating constraint objects.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, console: Console):
        """Initializes the RuleFactory.

        Args:
            console: An instance of the Console for logging and output,
                to be passed to rule handlers.
        """
        self._console = console
        self._selector_factory = SelectorFactory()
        self._constraint_factory = ConstraintFactory()

    def create(self, rule_config: dict[str, Any]) -> Rule:
        """Creates a specific rule instance based on its configuration.

        This method acts as a dispatcher. It determines whether the configuration
        describes a "short" pre-defined rule or a "full" custom rule with a
        selector/constraint pair, and then delegates to the appropriate
        creation logic.

        Args:
            rule_config: A dictionary parsed from the JSON rules file.

        Returns:
            An instance of an object that conforms to the Rule protocol.

        Raises:
            RuleParsingError: If the rule configuration is invalid, missing
                required keys, or specifies an unknown type.
        """
        rule_id = rule_config.get("rule_id")
        self._console.print(f"Start parsing rule ({rule_id}):\n{rule_config}", level=LogLevel.TRACE)
        try:
            if "type" in rule_config:
                self._console.print(f"Rule {rule_id} is shorted rule - {rule_config['type']}", level=LogLevel.DEBUG)
                config = _create_dataclass_from_dict(ShortRuleConfig, rule_config)
                return self._create_short_rule(config)

            elif "check" in rule_config:
                raw_selector_cfg = rule_config["check"]["selector"]
                raw_constraint_cfg = rule_config["check"]["constraint"]

                selector_cfg = _create_dataclass_from_dict(SelectorConfig, raw_selector_cfg)
                constraint_cfg = _create_dataclass_from_dict(ConstraintConfig, raw_constraint_cfg)

                selector = self._selector_factory.create(selector_cfg)
                constraint = self._constraint_factory.create(constraint_cfg)

                self._console.print(
                    f"Rule {rule_id} is general rule with: selector - "
                    f"{selector_cfg.type}, constraint - {raw_constraint_cfg['type']}",
                    level=LogLevel.DEBUG,
                )

                check_cfg = FullRuleCheck(selector=selector_cfg, constraint=constraint_cfg)
                self._console.print(f"Create FullRuleCheck: {check_cfg}", level=LogLevel.TRACE)

                config = FullRuleConfig(
                    rule_id=rule_config["rule_id"],
                    message=rule_config["message"],
                    check=check_cfg,
                    is_critical=rule_config.get("is_critical", False),
                )
                self._console.print(f"Create FullRuleConfig: {config}", level=LogLevel.TRACE)
                return FullRuleHandler(config, selector, constraint, self._console)
            else:
                self._console.print(f"Invalid syntax of rule: {rule_id}", level=LogLevel.WARNING)
                raise RuleParsingError("Rule must contain 'type' or 'check' key.", rule_id)
        except (TypeError, KeyError, RuleParsingError) as e:
            raise RuleParsingError(f"Invalid config for rule '{rule_id}': {e}", rule_id) from e

    def _create_short_rule(self, config: ShortRuleConfig) -> Rule:
        """Dispatches the creation of handlers for "short" rules.

        This private helper method acts as a registry for pre-defined, common
        validation checks like syntax or PEP8 linting. It maps a rule's 'type'
        string to a concrete Rule handler class.

        Args:
            config: The dataclass object containing the configuration for the
                short rule.

        Returns:
            An initialized instance of a concrete class that implements the
            Rule protocol.

        Raises:
            RuleParsingError: If the 'type' specified in the config does not
                correspond to any known short rule.
        """
        if config.type == "check_syntax":
            return CheckSyntaxRule(config, self._console)
        elif config.type == "check_linter_pep8":
            return CheckLinterRule(config, self._console)
        else:
            raise RuleParsingError(f"Unknown short rule type: '{config.type}'", config.rule_id)


class SelectorFactory:
    """Creates selector objects from raw dictionary configuration.

    This factory is responsible for instantiating the correct Selector object
    based on the 'type' field in a rule's selector configuration block. Each
    concrete selector specializes in finding a specific type of AST node.
    This class uses a static `create` method as it does not need to maintain
    any state.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self) -> None:
        pass

    @staticmethod
    def create(config: SelectorConfig) -> Selector:
        """Creates a specific selector instance based on its type.

        This method uses the 'type' field from the selector configuration
        to determine which concrete Selector class to instantiate.

        Args:
            config: The 'selector' block from a JSON rule.

        Returns:
            An instance of a class that conforms to the Selector protocol.
        """
        match config.type:
            case "function_def":
                return FunctionDefSelector(name=config.name, in_scope=config.in_scope)
            case "class_def":
                return ClassDefSelector(name=config.name, in_scope=config.in_scope)
            case "import_statement":
                return ImportStatementSelector(name=config.name, in_scope=config.in_scope)
            case "function_call":
                return FunctionCallSelector(name=config.name, in_scope=config.in_scope)
            case "assignment":
                return AssignmentSelector(name=config.name, in_scope=config.in_scope)
            case "usage":
                return UsageSelector(name=config.name, in_scope=config.in_scope)
            case "literal":
                return LiteralSelector(name=config.name, in_scope=config.in_scope)
            case "ast_node":
                return AstNodeSelector(node_type=config.node_type, in_scope=config.in_scope)
            case _:
                raise RuleParsingError(f"Unknown selector type: '{config.type}'")


class ConstraintFactory:
    """Creates constraint objects from raw dictionary configuration.

    This factory is responsible for instantiating the correct Constraint object
    based on the 'type' field in a rule's constraint configuration block.
    Each concrete constraint specializes in applying a specific logical check
    to a list of AST nodes. This class uses a static `create` method.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self) -> None:
        pass

    @staticmethod
    def create(config: ConstraintConfig) -> Constraint:
        """Creates a specific constraint instance based on its type.

        This method uses the 'type' field from the constraint configuration
        to determine which concrete Constraint class to instantiate.

        Args:
            config: The 'constraint' block from a JSON rule.

        Returns:
            An instance of a class that conforms to the Constraint protocol.
        """
        match config.type:
            case "is_required":
                return IsRequiredConstraint(count=config.count)
            case "is_forbidden":
                return IsForbiddenConstraint()
            case "must_inherit_from":
                return MustInheritFromConstraint(parent_name=config.parent_name)
            case "must_be_type":
                return MustBeTypeConstraint(expected_type=config.expected_type)
            case "must_have_args":
                return MustHaveArgsConstraint(count=config.count, names=config.names, exact_match=config.exact_match)
            case "name_must_be_in":
                return NameMustBeInConstraint(allowed_names=config.allowed_names)
            case "value_must_be_in":
                return ValueMustBeInConstraint(allowed_values=config.allowed_values)
            case _:
                raise RuleParsingError(f"Unknown constraint type: '{config.type}'")
