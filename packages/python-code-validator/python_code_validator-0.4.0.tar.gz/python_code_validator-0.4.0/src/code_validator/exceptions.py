"""Defines custom exceptions for the code validator application.

These custom exception classes allow for more specific error handling and
provide clearer, more informative error messages throughout the application.
"""


class CodeValidatorError(Exception):
    """Base exception for all custom errors raised by this application."""

    pass


class RuleParsingError(CodeValidatorError):
    """Raised when a validation rule in the JSON file is malformed or invalid.

    This error indicates a problem with the configuration of a rule, not with
    the code being validated.

    Attributes:
        rule_id (int | str | None): The ID of the rule that caused the error,
            if available.
    """

    def __init__(self, message: str, rule_id: int | str | None = None):
        """Initializes the RuleParsingError.

        Args:
            message (str): The specific error message describing the problem.
            rule_id (int | str | None): The ID of the problematic rule.
        """
        self.rule_id = rule_id
        if rule_id:
            super().__init__(f"Error parsing rule '{rule_id}': {message}")
        else:
            super().__init__(f"Error parsing rules file: {message}")


class ValidationFailedError(CodeValidatorError):
    """Raised to signal that the source code did not pass validation.

    Note:
        Currently, this exception is defined but not actively raised, as the
        application handles validation failure via exit codes in the CLI.
        It is kept for potential future use in a library context.
    """

    pass
