"""
This module provides functions for logging.

Functions:
    setup_logging: Configures logging for the CoMPAS navlib library.

Authors: Sebastián Rodríguez-Martínez
Contact: srodriguez@mbari.org
"""

import logging
from typing import Optional


class _NavlibFormatter(logging.Formatter):
    """
    Custom formatter for the CoMPAS navlib library.
    Formats the log messages with a configurable application name and format.
    """

    def __init__(
        self,
        app_name: str = "navlib",
        date_format: str = "%Y/%m/%d %H:%M:%S",
        fmt: Optional[str] = None,
    ):
        """
        Initialize the formatter.

        Args:
            app_name (str): Name of the application to display in logs
            date_format (str): Format string for timestamps
            fmt (str, optional): Custom format string. If None, uses default format.
        """
        self.app_name = app_name
        self.date_format = date_format

        if fmt is None:
            fmt = f"[%(levelname)s] %(asctime)s [{app_name}][%(name)s]: %(message)s"

        super().__init__(fmt=fmt, datefmt=date_format)

    def format(self, record):
        """
        Format the log record.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: Formatted log message
        """
        # Use the parent's format method which handles the format string
        return super().format(record)


def setup_logging(
    level: int = 2,
    app_name: str = "navlib",
    logger_name: Optional[str] = None,
    handler: Optional[logging.Handler] = None,
    formatter: Optional[logging.Formatter] = None,
    clear_existing: bool = True,
) -> logging.Logger:
    """
    Set up logging with configurable options.

    Args:
        level: Logging level. The options are:
            0: CRITICAL
            1: DEBUG
            2: INFO
            3: WARNING
            4: ERROR
            5: NOTSET
        app_name: Name of the application for log formatting
        logger_name: Name of the logger to configure. If None, configures root logger
        handler: Custom handler. If None, uses StreamHandler
        formatter: Custom formatter. If None, uses NavlibFormatter
        clear_existing: Whether to clear existing handlers

    Returns:
        logging.Logger: Configured logger instance

    Raises:
        ValueError: If the logging level is invalid or not an integer.
        TypeError: If the logger_name is not a string.
        TypeError: If the handler is not a logging.Handler instance.
        TypeError: If the formatter is not a logging.Formatter instance.

    Examples:
        >>> logger = setup_logging(level=2, app_name="my_app")
        >>> logger.info("This is an info message.")
        [INFO][2023/10/01 12:00:00][my_app][root]: This is an info message.
    """
    # Map logging level
    if not isinstance(level, int):
        raise ValueError("Logging level must be an integer.")

    level_map = {
        0: logging.CRITICAL,
        1: logging.DEBUG,
        2: logging.INFO,
        3: logging.WARNING,
        4: logging.ERROR,
        5: logging.NOTSET,
    }

    level = level_map.get(level)
    if level is None:
        raise ValueError(
            "Invalid logging level. Use 0-5 for CRITICAL, DEBUG, INFO, WARNING, ERROR, NOTSET respectively."
        )

    # Get the logger
    logger = logging.getLogger(logger_name)

    # Clear existing handlers if requested
    if clear_existing:
        logger.handlers.clear()

    # Create handler if not provided
    if handler is None:
        handler = logging.StreamHandler()

    # Create formatter if not provided
    if formatter is None:
        formatter = _NavlibFormatter(app_name=app_name)

    # Configure handler
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Set the logger level
    logger.setLevel(level)

    return logger
