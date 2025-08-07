import ast
import configparser
import os
from pathlib import Path

BEAUTILOG_INI_FILENAME = "beautilog.ini"


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.optionxform = str           # preserve case

        self.logger = {}
        self.file_logger = {}
        self.sections = {}
        self.load_defaults()

        ini_path = self.get_or_create_config_file()
        self._parse(ini_path)

    def load_defaults(self):
        default_config_path = Path(__file__).parent / BEAUTILOG_INI_FILENAME
        self._parse(default_config_path)

    def get_or_create_config_file(self) -> Path:
        cwd = Path.cwd()
        ini_path = cwd / BEAUTILOG_INI_FILENAME
        if not ini_path.exists():
            default_ini_path = Path(__file__).parent / BEAUTILOG_INI_FILENAME
            with open(default_ini_path, "r") as src, open(ini_path, "w") as dst:
                dst.write(src.read())

        return ini_path


    def _parse(self, ini_path: Path):
        self.config.read(ini_path)
        for section in self.config.sections():
            items = dict(self.config[section].items())
            # Try to parse values that look like lists or dicts
            for k, v in items.items():
                try:
                    items[k] = ast.literal_eval(v)
                except Exception:
                    items[k] = v

            if section == "logger":
                self.logger.update(items)
            elif section == "file_logger":
                self.file_logger.update(items)
            else:
                if section not in self.sections:
                    self.sections[section] = {}
                self.sections[section].update(items)

    def __getitem__(self, section):
        if section == "logger":
            return self.logger
        elif section == "file_logger":
            return self.file_logger
        return self.sections.get(section, {})

    def __repr__(self):
        return f"Config(logger={self.logger}, file_logger={self.file_logger}, sections={self.sections})"
