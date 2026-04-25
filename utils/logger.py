"""
Structured logging for the AI-Powered Payment Fraud Detection System.

Provides JSON-formatted logs for production observability and human-readable
console output for development.

PCI-DSS Requirement 10 reference:
    - All prediction requests are logged with transaction metadata.
    - High-risk predictions are logged at WARNING level.
    - No sensitive cardholder data (PAN, CVV) is ever logged.
"""

import logging
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from utils.config import settings


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for production use."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach extra fields if present (e.g., transaction_id, risk_level)
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """
    Create or retrieve a named logger with both console and file handlers.

    Args:
        name: Logger name — typically ``__name__`` of the calling module.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

    # ---- Console handler (human-readable) ----
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # ---- File handler (JSON-structured) ----
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger
