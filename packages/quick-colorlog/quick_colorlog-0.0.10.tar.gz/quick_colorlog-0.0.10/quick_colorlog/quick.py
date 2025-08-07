import logging
import sys
from typing import Optional, TextIO

from colorama import Back, Fore, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Track if we've already configured the root logger
_root_logger_configured = False


class ColorizedFormatter(logging.Formatter):
    """
    Custom formatter for colorizing log messages based on their level.
    """

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.WHITE + Back.RED,
    }

    log_format = (
        "%(asctime)s %(name)s[%(process)d] %(levelname)s" + Fore.RESET + " %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        super().__init__(fmt=self.log_format, datefmt=self.date_format)

    def format(self, record) -> str:
        message = super().format(record)
        # Apply color based on the log level and if there is an attached TTY
        if sys.stdout.isatty():
            message = self.LEVEL_COLORS.get(record.levelno, Fore.RESET) + message

        return message


def _has_colorized_handler(logger: logging.Logger, output: TextIO) -> bool:
    """
    Check if the logger already has a ColorizedFormatter handler for the given output.

    Args:
        logger: The logger to check.
        output: The output stream to match.

    Returns:
        True if a matching handler exists, False otherwise.
    """
    for handler in logger.handlers:
        if (
            isinstance(handler, logging.StreamHandler)
            and isinstance(handler.formatter, ColorizedFormatter)
            and handler.stream == output
        ):
            return True
    return False


def init_colors(
    level: int = logging.INFO,
    output: TextIO = sys.stderr,
    logger_name: Optional[str] = None,
    force_reinit: bool = False,
) -> logging.Logger:
    """
    Initialize a logger with colorized output.

    Args:
        level (int): The logging level (default is logging.INFO).
        output (TextIO): The output stream (default is sys.stderr).
        logger_name (Optional[str]): Name for the logger. If None, uses root logger.
        force_reinit (bool): If True, removes existing ColorizedFormatter handlers first.

    Returns:
        The configured logger instance.

    Note:
        Calling this function multiple times with the same parameters will not
        create duplicate handlers. Use force_reinit=True to reset the configuration.
    """
    global _root_logger_configured

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Track root logger configuration to prevent accidental double setup
    is_root = logger_name is None
    if is_root and _root_logger_configured and not force_reinit:
        return logger

    # Remove existing ColorizedFormatter handlers if force_reinit is True
    if force_reinit:
        handlers_to_remove = []
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and isinstance(
                handler.formatter, ColorizedFormatter
            ):
                handlers_to_remove.append(handler)

        for handler in handlers_to_remove:
            logger.removeHandler(handler)
            handler.close()

    # Check if we already have a ColorizedFormatter handler for this output
    if _has_colorized_handler(logger, output):
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(output)
    console_handler.setLevel(level)

    # Create formatter with colorized output and custom log format
    formatter = ColorizedFormatter()
    console_handler.setFormatter(formatter)

    # Add handler to the logger
    logger.addHandler(console_handler)

    # Mark root logger as configured
    if is_root:
        _root_logger_configured = True

    return logger


def reset_colors(logger_name: Optional[str] = None) -> None:
    """
    Remove all ColorizedFormatter handlers from the specified logger.

    Args:
        logger_name (Optional[str]): Name of the logger to reset. If None, resets root logger.
    """
    global _root_logger_configured

    logger = logging.getLogger(logger_name)

    # Remove all ColorizedFormatter handlers
    handlers_to_remove = []
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and isinstance(
            handler.formatter, ColorizedFormatter
        ):
            handlers_to_remove.append(handler)

    for handler in handlers_to_remove:
        logger.removeHandler(handler)
        handler.close()

    # Reset root logger configuration flag if resetting root logger
    if logger_name is None:
        _root_logger_configured = False


def get_colorized_logger(
    name: str,
    level: int = logging.INFO,
    output: TextIO = sys.stderr,
    propagate: bool = False,
) -> logging.Logger:
    """
    Get a named logger with colorized output.

    This is a convenience function that creates a named logger with colorized formatting.
    It's recommended to use named loggers instead of the root logger for better control.

    Args:
        name (str): Name for the logger.
        level (int): The logging level (default is logging.INFO).
        output (TextIO): The output stream (default is sys.stderr).
        propagate (bool): Whether the logger should propagate to parent loggers (default False).

    Returns:
        The configured logger instance.
    """
    logger = init_colors(level=level, output=output, logger_name=name)
    logger.propagate = propagate
    return logger


if __name__ == "__main__":
    # Configure the root logger
    init_colors(level=logging.DEBUG)

    # Example log messages with root logger
    root_logger = logging.getLogger()
    root_logger.debug("This is a debug message from root logger")
    root_logger.info("This is an info message from root logger")

    # Test that calling init_colors multiple times doesn't create duplicates
    print("\n--- Testing double initialization (should not duplicate logs) ---")
    init_colors(level=logging.DEBUG)  # This should not add another handler
    root_logger.info("This message should only appear once")

    # Example with named logger
    print("\n--- Named logger example ---")
    named_logger = get_colorized_logger("test.app", level=logging.DEBUG)
    named_logger.debug("This is a debug message from named logger")
    named_logger.info("This is an info message from named logger")
    named_logger.warning("This is a warning message from named logger")
    named_logger.error("This is an error message from named logger")
    named_logger.critical("This is a critical message from named logger")

    # Test reset functionality
    print("\n--- Testing reset functionality ---")
    reset_colors()  # Reset root logger
    root_logger.info("This message should not be colorized (after reset)")

    # Reconfigure
    init_colors(level=logging.DEBUG)
    root_logger.info("This message should be colorized again (after reinit)")
