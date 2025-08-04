import logging
import sys
from typing import TextIO


def setup_logging(level: int = logging.WARNING, stream: TextIO = sys.stderr) -> logging.Logger:
    """
    Configure MCP-NLP logging with level-based stream routing.

    Args:
        level: The minimum logging level to display (default: WARNING)
        stream: The stream to write logs to (default: sys.stderr)

    Returns:
        The configured logger instance
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to prevent duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add the level-dependent handler
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure specific loggers
    loggers = ["mcp-nlp", "mcp.server", "mcp.server.lowlevel.server"]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

    # Return the application logger
    return logging.getLogger("mcp-nlp")
