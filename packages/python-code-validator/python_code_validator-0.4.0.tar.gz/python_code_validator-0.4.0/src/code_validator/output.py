"""Handles all console output and logging for the application.

This module provides a centralized way to manage user-facing messages and
internal logging. It ensures that all output is consistent and can be
controlled via configuration (e.g., log levels, silent mode).
"""

import logging
import sys
from functools import wraps
from typing import Callable, Concatenate, Literal, ParamSpec, TypeVar

from .config import LogLevel

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = (
    "{asctime}.{msecs:03.0f} | "
    "{levelname:^8} | "
    "[{processName}({process})/{threadName}({thread})] | "
    "{filename}:{funcName}:{lineno} | "
    "{message}"
)

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def trace(self, message, *args, **kws):
    """Logs a message with TRACE level (below DEBUG).

    This method allows logging messages with a custom TRACE level,
    defined at level number 5. It only emits the log if the logger
    is enabled for this level.

    To enable usage, attach this method to the `logging.Logger` class:

        logging.Logger.trace = trace

    Args:
        self: logger instance.
        message: The log message format string.
        *args: Arguments to be merged into the message format string.
        **kws: Optional keyword arguments passed to the logger,
               e.g., `exc_info`, `stacklevel`, or `extra`.

    Returns:
        None
    """
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)


logging.Logger.trace = trace


def setup_logging(log_level: LogLevel) -> logging.Logger:
    """Configures the root logger for the application.

    Sets up the basic configuration for logging, including the level,
    message format, and date format.

    Args:
        log_level: The minimum level of logs to display.

    Returns:
        The configured root logger instance.
    """
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT, style="{")

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

    return root_logger


P = ParamSpec("P")
T_self = TypeVar("T_self")


def log_initialization(
    level: LogLevel | Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = LogLevel.TRACE,
    start_message: str = "Initializing {class_name}...",
    end_message: str = "{class_name} initialized.",
) -> Callable[[Callable[Concatenate[T_self, P], None]], Callable[Concatenate[T_self, P], None]]:
    """Decorator factory for logging the initialization of a class instance.

    This decorator wraps a class's `__init__` method to automatically log
    messages before and after the constructor's execution. It helps in
    observing the lifecycle of objects, especially complex ones, without
    cluttering the `__init__` method itself.

    The log messages can include a `{class_name}` placeholder, which will
    be replaced by the actual name of the class being initialized.

    Args:
        level: The logging level (e.g., `LogLevel.DEBUG`, `LogLevel.INFO`)
            at which the messages should be logged.
        start_message: the message string to log immediately before the
            `__init__` method is called. This string can contain the
            `{class_name}` placeholder.
        end_message: The message string to log immediately after the
            `__init__` method completes its execution. This string can
            contain the `{class_name}` placeholder.

    Returns:
        A decorator function that can be applied to an `__init__` method
        of a class.
    """

    def decorator(init_method: Callable[Concatenate[T_self, P], None]) -> Callable[Concatenate[T_self, P], None]:
        """The actual decorator function."""

        @wraps(init_method)
        def wrapper(self: T_self, *args: P.args, **kwargs: P.kwargs) -> None:
            """The wrapper function that adds logging around __init__."""
            class_name = self.__class__.__name__
            logger = logging.getLogger(self.__class__.__module__)
            level_num = logging.getLevelName(level if isinstance(level, LogLevel) else level)

            logger.log(level_num, start_message.format(class_name=class_name))
            result = init_method(self, *args, **kwargs)
            logger.log(level_num, end_message.format(class_name=class_name))

            return result

        return wrapper

    return decorator


class Console:
    """A centralized handler for printing messages to stdout and logging.

    This class abstracts all output operations, allowing for consistent
    formatting and easy control over verbosity (e.g., silent mode). It ensures
    that every user-facing message is also properly logged.

    Attributes:
        _logger (logging.Logger): The logger instance used for all log records.
        _is_quiet (bool): A flag to suppress printing to stdout.
        _stdout (TextIO): The stream to write messages to (defaults to sys.stdout).

    Example:
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> console = Console(logger)
        >>> console.print("This is an informational message.")
        This is an informational message.
        >>> console.print("This is a warning.", level="WARNING")
        This is a warning.
    """

    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, logger: logging.Logger, *, is_quiet: bool = False, show_verdict: bool = True):
        """Initializes the Console handler.

        Args:
            logger: The configured logger instance to use for logging.
            is_quiet: If True, suppresses output to stdout. Defaults to False.
            show_verdict: If False, suppresses showing verdicts. Default to True
        """
        self._logger = logger
        self._is_quiet = is_quiet
        self._show_verdict = show_verdict
        self._stdout = sys.stdout
        self._current_file_path: str = "<unknown>"  # For typo detection context

    def should_print(self, is_verdict: bool, show_user: bool) -> bool:
        """Decides whether a message should be printed to stdout based on console flags.

        Quiet mode (Q) suppresses all output if enabled. For non-verdict messages (¬V),
        printing is allowed only when show_user (O) is True. For verdict messages (V),
        printing is allowed only when show_verdict (S) is True.

        Mathematically:
            F = ¬Q ∧ ( (¬V ∧ O) ∨ (V ∧ S) )
        where
            Q = self._is_quiet,
            V = is_verdict,
            S = self._show_verdict,
            O = show_user.

        Proof sketch:
            1. If Q is True, then ¬Q = False ⇒ F = False (silent mode).
            2. If Q is False, split on V:
               a. V = False ⇒ F = ¬Q ∧ O;
               b. V = True  ⇒ F = ¬Q ∧ S.
            3. Combine branches into F = ¬Q ∧ ( (¬V ∧ O) ∨ (V ∧ S) ).

        Args:
            is_verdict: True if this message is a verdict; controls branch V.
            show_user: True if non-verdict messages should be printed; controls branch O.

        Returns:
            True if and only if the combined condition F holds, i.e. the message may be printed.
        """
        return not self._is_quiet and ((not is_verdict and show_user) or (is_verdict and self._show_verdict))

    def print(
        self,
        message: str,
        *,
        level: LogLevel | Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = LogLevel.TRACE,
        is_verdict: bool = False,
        show_user: bool = False,
        exc_info: bool = False,
    ) -> None:
        """Prints a message to stdout and logs it simultaneously.

        The message is always sent to the logger with the specified level. It is
        printed to the configured stdout stream only if the console is not in
        silent mode.

        Args:
            message: The string message to be displayed and logged.
            level: The logging level for the message. Accepts both LogLevel
                   enum members and their string representations.
                   Defaults to LogLevel.TRACE.
            is_verdict: If True, this message is considered a
                        verdict and its printing is controlled by the
                        console’s `show_verdict` flag. Defaults to False.
            show_user:  If True and `is_verdict=False`, allows
                        printing non-verdict messages to stdout. Defaults to
                        False.
            exc_info:   If True this work as loggings.exception("<message>").
        """
        level_num = logging.getLevelName(level if isinstance(level, LogLevel) else level)
        self._logger.log(level_num, message, stacklevel=2, exc_info=exc_info)

        if (not self._is_quiet) and ((not is_verdict and show_user) or (is_verdict and self._show_verdict)):
            print(message, file=self._stdout)

    def set_current_file_path(self, file_path: str) -> None:
        """Set the current file path for typo detection context.

        Args:
            file_path: Path to the file currently being validated
        """
        self._current_file_path = file_path
