# logwise

A colorful, modern terminal logger with support for rounded boxed messages, rich formatting, and contextual output — all with zero dependencies.

---

## 🚀 Features

- 🌈 ANSI-colored log levels (debug/info/warn/error/box)
- 📦 Custom `BOX` log level with **center-aligned**, **rounded box borders**
- 🧠 Smart handling of f-strings and printf-style logging
- 🧭 Logs include file name and line number
- 🪶 Lightweight, no dependencies

---

## 📦 Installation

```bash
pip install logwise
```

---

## 🛠️ Usage

```python
from logwise import logger

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")
logger.box("This is a boxed highlight")
```

---

## 📁 Example Output

```
DEBUG  2025-04-22 12:00:01.123 [DEBUG] This is a debug message (main.py:10)
INFO   2025-04-22 12:00:01.124 [INFO ] This is an info message (main.py:11)
WARN   2025-04-22 12:00:01.125 [WARN ] This is a warning (main.py:12)
ERROR  2025-04-22 12:00:01.126 [ERROR] This is an error (main.py:13)
BOX    2025-04-22 12:00:01.127 (main.py:14)
       ╭────────────────────────────╮
       │ This is a boxed highlight  │
       ╰────────────────────────────╯
```

---

## 🧩 Developer Notes

`logwise` uses a `CustomLogger` class built atop the Python `logging` module. You can plug it into existing logging flows, redirect output, or customize formatting as needed.

---

## 📄 License

MIT. See [LICENSE](./LICENSE).