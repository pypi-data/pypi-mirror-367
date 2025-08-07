"""
Provides a custom log formatter for a Logcat-style output.

This module contains the `LogFormatter` class, which is responsible for
taking a log record and formatting it into a colored, single-line message
resembling the output from Android's Logcat.
"""
import logging
import time

from logcatter.color import COLOR, COLOR_RESET


class LogFormatter(logging.Formatter):
    """
    A custom log formatter that mimics the style of Android's Logcat.

    This formatter creates log messages with the following structure:
    `YYYY-MM-DD HH:mm:ss SSS [L/tag] message`
    """

    ignore_color: bool = False

    def __init__(self, ignore_color: bool = False):
        super().__init__()
        self.ignore_color = ignore_color

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record into a colored, Logcat-style string.

        This method assembles the final log message, including the timestamp,
        log level initial, filename tag, and the core message. It also
        appends formatted exception and stack trace information if present.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log string.
        """
        asctime = self.formatTime(record)
        level = record.levelname.upper()[0]
        tag = record.filename
        message = record.getMessage()
        color = COLOR.get(record.levelno) if not self.ignore_color else ""
        color_reset = COLOR_RESET if not self.ignore_color else ""
        header = f"{asctime} [{level}/{tag}] "
        # Base message
        result = f"{color}{header}{message}{color_reset}"
        # Exception and errors
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if result[-1:] != '\n':
                result += '\n'
            result += f"{color}{header}{record.exc_text}{color_reset}"
        # Stack
        if record.stack_info:
            stack_messages = self.formatStack(record.stack_info).split("\n")
            for message in stack_messages:
                result += f"\n{color}{header}{message}{color_reset}"
        return result

    def formatTime(self, record, datefmt = None) -> str:
        """
        Formats the creation time of a log record to include milliseconds.

        Overrides the base `formatTime` to produce a timestamp in the format
        `YYYY-MM-DD HH:mm:ss.SSS`.

        Args:
            record (logging.LogRecord): The log record.
            datefmt (str | None): A `strftime`-compatible format string.
                If None, the default format is used.

        Returns:
            str: The formatted timestamp string.
        """
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = f"{t} {int(record.msecs):03d}"
        return s
