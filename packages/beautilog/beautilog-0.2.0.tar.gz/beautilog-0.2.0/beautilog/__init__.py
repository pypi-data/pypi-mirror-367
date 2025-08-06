from logging import Logger

# beautilog/__init__.py
from .beauti_logger import get_logger
from .constants import TERMINAL_COLORS
from .custom_handlers import ColoredConsoleHandler

# Initialize logger at import time
logger: Logger = get_logger()

# Optional: expose utility functions if needed later
__all__ = [
    "ColoredConsoleHandler",
    "TERMINAL_COLORS",
    "get_logger",
    "logger"
]
