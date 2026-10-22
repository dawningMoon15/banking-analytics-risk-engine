"""Logging configuration for Banking Customer Analytics & Risk Engine."""

import logging
import os
from pathlib import Path


def get_logger(name: str, log_file: str = "logs/pipeline.log", level: str = "INFO") -> logging.Logger:
    """Configures and returns a structured logger.

    Logs to both console (INFO level by default) and a persistent log file (DEBUG level).

    Args:
        name: Name of the logger, typically __name__ of calling module.
        log_file: Relative or absolute path to log file.
        level: Log level string (e.g. 'INFO', 'DEBUG').

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if logger was already created
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler (DEBUG level for full trace)
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path))
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler (configurable level, default INFO)
        console_handler = logging.StreamHandler()
        console_level = getattr(logging, level.upper(), logging.INFO)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
