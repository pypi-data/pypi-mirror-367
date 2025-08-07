"""
Provides a static, Android Logcat-style logging interface.

This module offers a simple, zero-configuration facade over Python's standard
logging module, designed to be instantly familiar to Android developers.
"""
import sys
import multiprocessing
import functools
from typing import Union
import logging
from logging.handlers import QueueHandler
from contextlib import contextmanager

from logcatter.formatter import LogFormatter
from logcatter.logcat import Logcat
from logcatter.level import LEVEL_VERBOSE, LEVEL_DEBUG, LEVEL_INFO, LEVEL_WARNING, LEVEL_ERROR, LEVEL_FATAL
from logcatter.command import COMMAND_SET_LEVEL


class Log:
    """
    A static utility class that provides an Android Logcat-like logging interface.

    **IMPORTANT**

    Use `Log.init()` very first of your code, to initialize the logging system. And
    use `Log.dispose()` very last of your code, to gracefully dispose this.

    If you want to use multiprocessing, use `Log.pool_init` as an initializer.

    .. code-block:: python

        Log.init()
        with multiprocessing.Pool(processes=2, initializer=Log.pool_init) as pool:
            # Your code

    This class is not meant to be instantiated. It offers a set of static methods
    (e.g., `d`, `i`, `w`, `e`) that wrap the standard Python `logging` module
    to provide a simple, zero-configuration logging experience. It automatically
    configures a logger that outputs messages in a format similar to Android's
    Logcat, including automatic tagging with the calling filename.
    """

    VERBOSE = LEVEL_VERBOSE
    DEBUG = LEVEL_DEBUG
    INFO = LEVEL_INFO
    WARNING = LEVEL_WARNING
    ERROR = LEVEL_ERROR
    FATAL = LEVEL_FATAL

    _log_queue: Union['multiprocessing.Queue', None] = None
    _listener_process: Union['multiprocessing.Process', None] = None

    @staticmethod
    def _listener_configurer(level: int | str):
        """
        [Internal] Configures the logger for the listener process.
        This version is self-contained and does not depend on other Log methods.
        """
        logger = logging.getLogger(Logcat.NAME)
        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setFormatter(LogFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)

    @staticmethod
    def _listener_process_target(queue: multiprocessing.Queue, level: int | str):
        """
        [Internal] The target function for the listener process.
        It waits for log records on the queue and processes them.
        """
        Log._listener_configurer(level)
        logger = logging.getLogger(Logcat.NAME)
        while True:
            try:
                item = queue.get()
                if item is None:
                    break
                if isinstance(item, tuple):
                    command, value = item
                    if command == COMMAND_SET_LEVEL:
                        logger.setLevel(value)
                    continue
                if logger.isEnabledFor(item.levelno):
                    logger.handle(item)
            except Exception:
                import sys, traceback
                print('[logcatter] Error in logging listener process:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

    @staticmethod
    def _worker_configurer():
        """
        [Internal] Configures logging for a worker process.
        It removes all existing handlers and adds a QueueHandler.
        This now reads the queue from the class's static variable.
        """
        if Log._log_queue is None:
            return
        logger = logging.getLogger(Logcat.NAME)
        if logger.hasHandlers():
            logger.handlers.clear()

        qh = QueueHandler(Log._log_queue)
        logger.addHandler(qh)
        logger.setLevel(Log.VERBOSE)

    @staticmethod
    def _enable_multiprocessing(level: int | str = VERBOSE):
        """
        Initializes the logging system for a multiprocessing environment.
        This must be called once from the main process.

        It starts a dedicated listener process that handles all log records
        sent from other processes.

        Args:
            level: The global logging level for the entire application.
        """
        if Log._listener_process is not None:
            return

        Log._log_queue = multiprocessing.Queue(-1)
        Log._listener_process = multiprocessing.Process(
            target=Log._listener_process_target,
            args=(Log._log_queue, level)
        )
        Log._listener_process.daemon = True
        Log._listener_process.start()
        Log._worker_configurer()

    @staticmethod
    def _disable_multiprocessing():
        """
        Shuts down the logging listener process gracefully.
        This should be called at the end of the main script to ensure
        all logs are flushed.
        """
        if Log._listener_process is None:
            return
        if Log._log_queue:
            Log._log_queue.put(None)
        if Log._listener_process:
            Log._listener_process.join()
        Log._listener_process = None
        Log._log_queue = None

    @staticmethod
    def init():
        logging.addLevelName(Log.VERBOSE, "VERBOSE")
        logging.addLevelName(Log.FATAL, "FATAL")
        Log._enable_multiprocessing()

    @staticmethod
    def dispose():
        Log._disable_multiprocessing()

    @staticmethod
    def init_pool(queue: Union['multiprocessing.Queue', None] = None, worker_id: int = 0):
        """
        A helper to be used as the initializer for `multiprocessing.Pool`.
        Example: multiprocessing.Pool(initializer=Log.pool_init)
        """
        if queue is not None:
            Log._log_queue = queue
        Log._worker_configurer()

    @staticmethod
    def init_worker() -> callable:
        """
        Returns a pre-configured worker_init_fn for PyTorch DataLoader.

        This handles the complexity of passing the log queue to worker processes,
        encapsulating the functools.partial call.

        Returns:
            A callable function suitable for the `worker_init_fn` argument.

        Raises:
            RuntimeError: If `Log.init()` has not been called first.
        """
        log_queue = Log.get_queue()
        if log_queue is None:
            raise RuntimeError(
                "Log.init() must be called before get_worker_init_fn()."
            )
        return functools.partial(Log.init_pool, queue=log_queue)

    @staticmethod
    def get_queue() -> Union['multiprocessing.Queue', None]:
        """
        Returns the internal log queue.
        Useful for passing the queue to other modules or initializers.
        """
        return Log._log_queue

    @staticmethod
    def get_logger() -> logging.Logger:
        """
        Retrieves the singleton logger instance for the application.

        On the first call, it initializes the logger with a `StreamHandler` and
        the custom `LogFormatter`. Subsequent calls return the same logger instance
        without adding more handlers, preventing duplicate log messages.

        Returns:
            logging.Logger: The configured logger instance.
        """
        logger = logging.getLogger(Logcat.NAME)
        # Register stream handler
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setFormatter(LogFormatter())
            logger.addHandler(handler)
        return logger

    @staticmethod
    def set_level(level: int | str):
        """
        Sets the logging level for the application's logger.

        Messages with a severity lower than `level` will be ignored.

        Args:
            level (int | str): The minimum level of severity to log.
                Can be an integer constant (e.g., `logging.INFO`) or its string
                representation (e.g., "INFO").
        """
        if Log._log_queue:
            command = (COMMAND_SET_LEVEL, level)
            Log._log_queue.put(command)
        else:
            Log.get_logger().setLevel(level)

    @staticmethod
    def save(filename: str, mode="w"):
        """
        Saves the log to a file.
        :param filename: Path of the file to save to.
        :param mode: Mode to open the file with. Default is 'w'.
        """
        handler = logging.FileHandler(filename, mode=mode)
        handler.setFormatter(LogFormatter(ignore_color=True))
        Log.get_logger().addHandler(handler)

    @staticmethod
    def is_verbose():
        """
        Checks the logging level is `Log.VERBOSE` or below.
        :return:
            bool: `True` when the level is `Log.VERBOSE` or below, `False` otherwise.
        """
        return Log.get_logger().level <= Log.VERBOSE

    @staticmethod
    def is_quiet():
        """
        Checks the logging level is `Log.WARNING` or above.
        :return:
            bool: `True` when the level is `Log.WARNING` or above, `False` otherwise.
        """
        return Log.get_logger().level >= Log.WARNING

    @staticmethod
    def is_silent():
        """
        Checks the logging level is greater than `Log.FATAL`.
        :return:
            bool: `True` when the level is greater than `Log.FATAL`, `False` otherwise.
        """
        return Log.get_logger().level > Log.FATAL

    class _PrintLogger:
        """
        An internal file-like object that redirects writes to the Log utility.
        It buffers text until a newline is received, then logs the complete line.
        """

        def __init__(
                self,
                level: int,
                *args,
                **kwargs,
        ):
            self.level = level
            self.args = args
            self.kwargs = kwargs
            self._buffer = ""
            self.stacklevel = 3

        def write(self, text: str):
            """
            Receives text from a print call, buffers it, and logs complete lines.
            """
            if not text:
                return

            self._buffer += text
            if '\n' in self._buffer:
                lines = self._buffer.split('\n')
                self._buffer = lines.pop()
                for line in lines:
                    if line:
                        Log._log(
                            self.level,
                            line,
                            *self.args,
                            stacklevel=self.stacklevel,
                            **self.kwargs,
                        )

        def flush(self):
            """
            Logs any remaining text in the buffer. Called when the context exits.
            """
            if self._buffer:
                Log._log(
                    self.level,
                    self._buffer,
                    *self.args,
                    stacklevel=self.stacklevel,
                    **self.kwargs,
                )
                self._buffer = ""

    @staticmethod
    @contextmanager
    def redirect(
            stdout: int | None = VERBOSE,
            stderr: int | None = None,
            show_stdout_stack: bool = False,
            show_stderr_stack: bool = False,
    ):
        """
        Log `print` message with the given level in context

        Args:
            :param stdout: Level of the message.
            :param stderr: Level of the error message.
            :param show_stdout_stack: Whether show the stacktrace or not for the message.
            :param show_stderr_stack: Whether show the stacktrace or not for the error.
        """
        # Print
        if stdout:
            original_stdout = sys.stdout
            buffer_out = Log._PrintLogger(stdout, s=show_stdout_stack)
            sys.stdout = buffer_out
        # Error
        if stderr:
            original_stderr = sys.stderr
            buffer_err = Log._PrintLogger(stderr, s=show_stderr_stack)
            sys.stderr = buffer_err

        try:
            yield
        finally:
            if stdout:
                buffer_out.flush()
                sys.stdout = original_stdout
            if stderr:
                buffer_err.flush()
                sys.stderr = original_stderr

    @staticmethod
    def _log(
            level: int,
            msg: str,
            *args,
            stacklevel: int = 3,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the given level.

        Args:
            :param level: Level of the message.
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        messages = msg.split('\n')
        for index, message in enumerate(messages):
            Log.get_logger().log(
                level,
                message,
                *args,
                stacklevel=stacklevel,
                exc_info=e if index == len(messages)-1 else None,
                stack_info=s if index == len(messages)-1 else False,
                **kwargs,
            )

    @staticmethod
    def v(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the VERBOSE level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.VERBOSE,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def d(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the DEBUG level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.DEBUG,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def i(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the INFO level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.INFO,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def w(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the WARNING level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.WARNING,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def e(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the ERROR level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.ERROR,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )

    @staticmethod
    def f(
            msg: str,
            *args,
            e: object | None = None,
            s: bool = False,
            **kwargs,
    ):
        """
        Logs a message with the CRITICAL level.

        Args:
            :param msg: The message to be logged.
            :param e: Exception object to logged together.
            :param s: Whether stacktrace or not
        """
        Log._log(
            Log.FATAL,
            msg,
            *args,
            stacklevel=3,
            e=e,
            s=s,
            **kwargs,
        )
