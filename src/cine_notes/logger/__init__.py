import logging
import os
import sys
from datetime import datetime
from from_root import from_root

"""
Logger configuration module for CineNotes application.

This module sets up logging with the following features:
- Timestamped log files in a dedicated logs directory
- Detailed log format with timestamp, logger name, level and message
- Debug level logging enabled
- Automatic log directory creation

The log files are named with the pattern: MM_DD_YYYY_HH_MM_SS.log
"""

try:
    # Generate timestamped log filename
    LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

    # Configure log directory
    log_dir = 'logs'
    logs_path = os.path.join(from_root(), log_dir, LOG_FILE)

    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        filename=logs_path,
        format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

except Exception as e:
    from cine_notes.exception import CineNotesException
    raise CineNotesException(
        "Failed to initialize logging configuration",
        sys
    )