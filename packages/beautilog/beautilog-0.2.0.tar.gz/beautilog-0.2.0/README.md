# 🌟 Beautilog

**Beautilog** is a Python logging library for beautiful, color-coded terminal output with support for custom log levels, log rotation, and simple configuration through a JSON file.

![Example output](example.png)

---

## 📦 Installation

Install from PyPI:

```bash
pip install beautilog
```

Or, for development:

```bash
git clone https://github.com/yourname/beautilog.git
cd beautilog
pip install -e .
```

---

### 🧪 Quick Test

```bash
python -c 'from beautilog import logger; logger.info("Hello from Beautilog!")'
```

---

## ⚙️ Configuration: `beauti-log.json`

Beautilog looks for a `beauti-log.json` file in your working directory or library path. Example config:

```json
{
  "save_to_file": true,
  "file_logger": {
    "log_file_path": "beauti-run.log",
    "backup_count": 5,
    "max_bytes": 104857600,
    "log_level": "DEBUG"
  },
  "suppress_other_loggers": true,
  "log_level": "INFO",
  "custom_levels": {
    "NOTIFICATION": 12
  },
  "level_colors": {
    "CRITICAL": "RED",
    "ERROR": "BRIGHT_RED",
    "WARNING": "YELLOW",
    "INFO": "CYAN",
    "NOTIFICATION": "GREEN",
    "DEFAULT": "RESET"
  }
}
```

### 🔧 Config Keys

| Key                      | Description                                        |
| ------------------------ | -------------------------------------------------- |
| `save_to_file`           | Enable/disable file logging                        |
| `file_logger`            | File logging settings (path, size, backups)        |
| `log_level`              | Default log level (`DEBUG`, `INFO`, etc.)          |
| `custom_levels`          | Define your own log levels like `NOTIFICATION`     |
| `level_colors`           | Customize terminal colors per level                |
| `suppress_other_loggers` | Hide noisy loggers like `asyncio`, `urllib3`, etc. |

---

## 🚀 Example Usage

```python
from beautilog import logger

logger.info("This is an info message.")
logger.warning("This is a warning!")
logger.error("This is an error!")

# Custom level
logger.notification(f"Custom NOTIFICATION level {logger.NOTIFICATION} message")
```

✅ Custom levels are automatically injected and styled from your config.

---

## 🎨 Supported Colors

Use any of these in `level_colors`:

* Basic: `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `WHITE`
* Bright: `BRIGHT_RED`, `BRIGHT_YELLOW`, etc.
* Control: `RESET` (returns to default terminal color)

---

## 📂 File Logging

If `"save_to_file": true`, logs are saved to `beauti-run.log` using a rotating file handler.


---

## 📜 License

Licensed under the **Apache License 2.0** — free for personal and commercial use.

---