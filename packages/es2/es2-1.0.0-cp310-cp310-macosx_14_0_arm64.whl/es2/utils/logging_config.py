import os
import sys

from loguru import logger

# Configure logger based on environment variable
log_level = os.getenv("ES2_LOG_LEVEL", "").upper()
if log_level in ["DEBUG", "INFO", "ERROR"]:
    logger.add(sys.stdout, format="{time:YY-MM-DD at HH:mm:ss} | {level} | {message}", level=log_level)
else:
    logger.disable("")

# Export the logger for use in other modules
__all__ = ["logger"]
