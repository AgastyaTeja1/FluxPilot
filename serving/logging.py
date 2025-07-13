# serving/logging.py

import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """
    Configure root logger to output structured JSON logs to stdout.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # Create and configure JSON formatter
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    log_handler.setFormatter(formatter)

    # Attach handler
    root_logger.addHandler(log_handler)
