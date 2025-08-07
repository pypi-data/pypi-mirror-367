import logging
import sys
from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import functools
import inspect
import time
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install as install_rich_traceback
from rich.theme import Theme

# Install rich traceback handling
install_rich_traceback(show_locals=True)

# Custom theme for rich
CUSTOM_THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "critical": "red reverse",
        "success": "green",
        "timestamp": "dim blue",
        "logger.name": "blue",
        "function": "magenta",
    }
)

# Create rich console with custom theme
console = Console(theme=CUSTOM_THEME)


class CustomFormatter(logging.Formatter):
    """Custom formatter with color support and structured format."""

    def __init__(self, include_path: bool = True):
        self.include_path = include_path
        super().__init__()

    def format(self, record):
        # Create copies of the record to avoid modifying the original
        record = logging.makeLogRecord(record.__dict__)

        # Add timestamp
        record.timestamp = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Add calling function and line number if available
        if record.pathname and record.lineno:
            if self.include_path:
                record.source = f"{Path(record.pathname).name}:{record.lineno}"
            else:
                record.source = f"{record.funcName}:{record.lineno}"
        else:
            record.source = "unknown"

        # Format the message
        record.message = record.getMessage()

        # Construct the log message
        parts = [
            f"[timestamp]{record.timestamp}[/]",
            f"[logger.name]{record.name}[/]",
            f"[function]{record.source}[/]",
            f"[{record.levelname.lower()}]{record.message}[/]",
        ]

        # Add exception info if present
        if record.exc_info:
            parts.append(self.formatException(record.exc_info))

        return " | ".join(parts)


def get_logger(
    name: str,
    level: Union[str, int] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    include_path: bool = True,
) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Name of the logger
        level: Logging level
        log_file: Optional file path to save logs
        include_path: Whether to include full path in log messages

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler with rich support
    console_handler = RichHandler(
        console=console,
        show_time=False,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )
    console_handler.setFormatter(CustomFormatter(include_path=include_path))
    logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(CustomFormatter(include_path=True))
        logger.addHandler(file_handler)

    return logger


def log_execution_time(func=None, *, logger=None, level=logging.INFO):
    """
    Decorator to log function execution time.

    Args:
        func: Function to decorate
        logger: Logger instance to use (if None, creates one based on module name)
        level: Logging level for the timing message
    """
    if func is None:
        return functools.partial(log_execution_time, logger=logger, level=level)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get or create logger
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)

        # Log function call
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.log(level, f"{func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.exception(
                f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}"
            )
            raise

    return wrapper


# Example usage for the entire repo:
"""
# In your base initialization file (__init__.py):
from .utils.logging import get_logger, log_execution_time

# Create a global logger instance
logger = get_logger(__name__, log_file="logs/app.log")

# In other modules:
from your_package import logger

# Usage in functions:
logger.info("Starting process")
logger.warning("Resource usage high")
logger.error("Failed to process", exc_info=True)
logger.success("Task completed successfully")  # Custom level

# Using the timing decorator:
@log_execution_time
def long_running_function():
    # Your code here
    pass

# Or with custom logger/level:
@log_execution_time(logger=custom_logger, level=logging.DEBUG)
def another_function():
    # Your code here
    pass
"""


# Add custom success level
def _success(self, message, *args, **kwargs):
    """Log 'SUCCESS' level messages (between INFO and WARNING)"""
    self.log(25, message, *args, **kwargs)


# Add success level to Logger class
SUCCESS_LEVEL = 25  # Between INFO and WARNING
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.Logger.success = _success
