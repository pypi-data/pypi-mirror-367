# fancy_log/logger_setup.py
import copy
import logging

from .constants import TERMINAL_COLORS


class ColoredConsoleHandler(logging.StreamHandler):
    def __init__(self, stream, level_colors):
        super().__init__(stream)
        self.level_colors = level_colors

    def emit(self, record):
        myrecord = copy.copy(record)
        levelname = myrecord.levelname.upper()
        color_name = self.level_colors.get(levelname, self.level_colors.get("DEFAULT", "RESET"))
        color_code = TERMINAL_COLORS.get(color_name.upper(), TERMINAL_COLORS["RESET"])
        myrecord.msg = color_code + str(myrecord.msg) + TERMINAL_COLORS["RESET"]
        super().emit(myrecord)


class ForceLevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        # Change the level of the record to the forced one
        record.levelno = self.level
        record.levelname = logging.getLevelName(self.level)
        return True
