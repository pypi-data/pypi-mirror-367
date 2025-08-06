"""A flexible framework for static validation of Python code.

This package provides a comprehensive toolkit for statically analyzing Python
source code based on a declarative set of rules defined in a JSON format. It
allows for checking syntax, style, structure, and constraints without
executing the code.

The primary entry point for using this package programmatically is the
`StaticValidator` class.

Example:
    A minimal example of using the validator as a library.

    .. code-block:: python

        from code_validator import StaticValidator, AppConfig, LogLevel
        from code_validator.output import Console, setup_logging
        from pathlib import Path

        # Basic setup
        logger = setup_logging(LogLevel.INFO)
        console = Console(logger)
        config = AppConfig(
            solution_path=Path("path/to/solution.py"),
            rules_path=Path("path/to/rules.json"),
            log_level=LogLevel.INFO,
            is_silent=False,
            stop_on_first_fail=False
        )

        # Run validation
        validator = StaticValidator(config, console)
        is_valid = validator.run()

        if is_valid:
            print("Validation Passed!")

Attributes:
    __version__ (str): The current version of the package.
    __all__ (list[str]): The list of public objects exposed by the package.

"""

from .config import AppConfig, ExitCode, LogLevel
from .core import StaticValidator
from .exceptions import RuleParsingError, ValidationFailedError

__all__ = [
    "StaticValidator",
    "AppConfig",
    "ExitCode",
    "LogLevel",
    "ValidationFailedError",
    "RuleParsingError",
]

__version__ = "0.4.0"
