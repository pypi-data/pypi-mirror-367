import logging
import os
import shutil
import textwrap
from typing import Any

from wcwidth import wcswidth

BOX_LEVEL = 5
logging.addLevelName(BOX_LEVEL, "BOX")
logging.addLevelName(logging.WARNING, "WARN")


class CustomLogger:
    bold_cyan = "\x1b[36;1m"
    bold_green = "\x1b[1;32m"
    bold_yellow = "\x1b[1;33m"
    bold_red = "\x1b[31;1m"
    bold_white = "\x1b[1;39m"
    reset = "\x1b[0m"

    base_format = "%(asctime)s.%(msecs)03d [%(levelname)-5s] %(message)s (%(package_file)s:%(lineno)d)"
    box_format = "%(asctime)s.%(msecs)03d (%(package_file)s:%(lineno)d)\n%(message)s"

    class Formatter(logging.Formatter):
        def __init__(self, outer, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.outer = outer
            self._box_formatter = logging.Formatter(outer.box_format, datefmt='%Y-%m-%d %H:%M:%S')

        def format(self, record):
            record.filename = os.path.basename(record.pathname).split('.')[0]

            if record.name == "__main__":
                try:
                    pathname = record.pathname
                    parent_dir = os.path.basename(os.path.dirname(pathname))
                    script_name = os.path.basename(pathname).split('.')[0]

                    if parent_dir and parent_dir not in {'Documents', 'Users', 'home', '.'}:
                        record.package_file = f"{parent_dir}.{script_name}"
                    else:
                        record.package_file = script_name
                except Exception:
                    record.package_file = record.filename
            else:
                record.package_file = record.name

            if record.levelno == BOX_LEVEL:
                return self.outer.bold_white + self._box_formatter.format(record) + self.outer.reset

            if record.levelno == logging.DEBUG:
                fmt = self.outer.bold_cyan + self.outer.base_format + self.outer.reset
            elif record.levelno == logging.INFO:
                fmt = self.outer.bold_green + self.outer.base_format + self.outer.reset
            elif record.levelno == logging.WARNING:
                fmt = self.outer.bold_yellow + self.outer.base_format + self.outer.reset
            elif record.levelno == logging.ERROR:
                fmt = self.outer.bold_red + self.outer.base_format + self.outer.reset
            else:
                fmt = self.outer.bold_white + self.outer.base_format + self.outer.reset

            self._style._fmt = fmt
            return super().format(record)

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(BOX_LEVEL)

        handler = logging.StreamHandler()
        handler.setLevel(BOX_LEVEL)
        handler.setFormatter(self.Formatter(self, datefmt='%Y-%m-%d %H:%M:%S'))

        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        self.logger.propagate = False

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs, stacklevel=2)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs, stacklevel=2)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs, stacklevel=2)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs, stacklevel=2)

    def box(self, msg: Any, *args, **kwargs):
        """Log a message inside a decorative box with proper centering and wrapping."""
        if args:
            msg = str(msg) % args
        else:
            msg = str(msg)

        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80  # fallback

        # Clamp width
        box_width = min(120, max(20, term_width))
        content_width = box_width - 4  # for borders and spaces

        wrapped_lines = []
        for line in msg.splitlines():
            if not line.strip():
                wrapped_lines.append("")
            else:
                wrapped = textwrap.wrap(
                    line,
                    width=content_width,
                    break_long_words=True,
                    break_on_hyphens=True
                )
                wrapped_lines.extend(wrapped or [""])

        top = '╭' + '─' * (box_width - 2) + '╮'
        bottom = '╰' + '─' * (box_width - 2) + '╯'

        middle = []
        for line in wrapped_lines:
            display_len = wcswidth(line)
            if display_len is None:
                display_len = len(line)
            if display_len > content_width:
                # Truncate with ellipsis
                line = line[:max(0, content_width - 3)] + "..."
                display_len = wcswidth(line)
                if display_len is None:
                    display_len = len(line)

            pad_left = (content_width - display_len) // 2
            pad_right = content_width - display_len - pad_left
            centered = ' ' * pad_left + line + ' ' * pad_right
            middle.append(f"│ {centered} │")

        full_box = '\n'.join([top] + middle + [bottom])

        kwargs.setdefault('stacklevel', 2)
        self.logger.log(BOX_LEVEL, full_box, **kwargs)

    def get_logger(self):
        return self.logger
