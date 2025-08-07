# fancy_log/logger_setup.py
import copy
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from tqdm import tqdm

from .config import Config
from .constants import TERMINAL_COLORS
from .custom_handlers import ColoredConsoleHandler, ForceLevelFilter


def get_logger() -> logging.Logger:
    config = Config()
    logger = logging.getLogger()

    if config.logger.get("suppress_existing_loggers", False):
        logger.handlers.clear()

    for mute_loggger_name in config.logger.get("disabled_loggers", []):
        mute_logger = logging.getLogger(mute_loggger_name)
        mute_logger.setLevel(logging.CRITICAL)
        mute_logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s : %(levelname)s : %(name)s : %(message)s',
        datefmt='%m/%d/%y %I:%M:%S %p'
    )

    if config.logger.get("save_to_file", True):
        file_handler = RotatingFileHandler(
            config.file_logger.get("log_file_path", "fancy-run.log"),
            mode='a',
            maxBytes=config.file_logger.get("max_bytes", 10485760),  # Default 100 MB
            backupCount=config.file_logger.get("backup_count", 5),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, config.file_logger.get("log_level", "DEBUG").upper(), logging.DEBUG))
        logger.addHandler(file_handler)

    def write(self, x):
        if len(x.rstrip()) > 0:
            tqdm.write(x, file=self.file, end='')
    out_stream = type("TqdmStream", (), {'file': sys.stdout, 'write': write})()

    console_handler = ColoredConsoleHandler(out_stream, config.sections.get("level_colors", {}))
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, config.logger.get("log_level", "INFO").upper(), logging.INFO))

    logger.addHandler(console_handler)
    logger.setLevel(getattr(logging, config.logger.get("log_level", "INFO").upper(), logging.INFO))

    for level_name, level_value in config.sections.get("custom_levels", {}).items():
        logging.addLevelName(level_value, level_name.upper())
        setattr(logging, level_name.upper(), level_value)
        setattr(logger, level_name.upper(), level_value)
        setattr(logger, level_name.lower(), lambda msg, level=level_value: logger.log(level, msg))


    for logger_name, level in config.sections.get("redirected_loggers", {}).items():
        redirected_logger = logging.getLogger(logger_name)
        stream_handler = logging.StreamHandler(out_stream)
        stream_handler.addFilter(ForceLevelFilter(getattr(logging, level.upper(), logging.INFO)))
        stream_handler.setFormatter(formatter)
        redirected_logger.addHandler(stream_handler)

    return logger
