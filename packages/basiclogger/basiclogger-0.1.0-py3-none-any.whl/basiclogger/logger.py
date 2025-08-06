import logging
from typing import Literal, Any, Optional
import time
from functools import wraps
import asyncio

class Logger:
    DEBUG: Literal[10] = logging.DEBUG
    INFO: Literal[20] = logging.INFO
    SUCCESS: Literal[21] = 21
    TRACE: Literal[25] = 25
    WARNING: Literal[30] = logging.WARNING
    ERROR: Literal[40] = logging.ERROR
    CRITICAL: Literal[50] = logging.CRITICAL

    LogLevel = Literal[DEBUG, INFO, SUCCESS, TRACE, WARNING, ERROR, CRITICAL]

    class Formatter(logging.Formatter):
        COLOR_CODES = {
            "DEBUG": "\033[96m",
            "INFO": "\033[34m",
            "SUCCESS": "\033[38;5;107m",
            "TRACE": "\033[95m",
            "WARNING": "\033[38;5;220m",
            "ERROR": "\033[31;5;160m",
            "CRITICAL": "\033[38;5;196m",
        }
        RESET = "\033[0m"

        def __init__(self, format_str: str):
            super().__init__(format_str)

        def format(self, record: logging.LogRecord) -> str:
            log_color = self.COLOR_CODES.get(
                record.levelname, self.COLOR_CODES["INFO"]
            )
            message = logging.Formatter.format(self, record)
            return f"{log_color}{message}{self.RESET}"

    def __init__(
        self,
        name: Optional[str] = None,
        level: LogLevel = TRACE,
        format_str: str = "%(asctime)s %(levelname)-8s %(message)s",
    ):
        logging.addLevelName(21, "SUCCESS")
        logging.addLevelName(25, "TRACE")

        self.name = name or "root"
        self.root_log: logging.Logger = logging.getLogger(self.name)
        self.root_log.handlers = []
        self.root_log.setLevel(level)
        self.root_log.propagate = False

        formatter = Logger.Formatter(format_str)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.root_log.addHandler(console_handler)

        file_handler = logging.FileHandler(f"{self.name}.log", mode="a", encoding="utf-8")
        file_formatter = logging.Formatter(format_str)
        file_handler.setFormatter(file_formatter)
        self.root_log.addHandler(file_handler)

        setattr(self.root_log, 'trace', self.trace)
        setattr(self.root_log, 'success', self.success)
        setattr(self.root_log, 'set_level', self.set_level)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.root_log.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.root_log.info(message, *args, **kwargs)

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.root_log.log(21, message, *args, **kwargs)

    def trace(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.root_log.log(25, message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.root_log.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.root_log.error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.root_log.critical(message, *args, **kwargs)

    def set_level(self, level: LogLevel) -> None:
        self.root_log.setLevel(level)
        level_name = logging.getLevelName(level).upper()

        self.debug(f"Log level set to {level_name}.")
        self.info(f"Log level set to {level_name}.")
        self.success(f"Log level set to {level_name}.")
        self.trace(f"Log level set to {level_name}.")
        self.warning(f"Log level set to {level_name}.")
        self.error(f"Log level set to {level_name}.")
        self.critical(f"Log level set to {level_name}.")


def log_time(_func=None, *, trace_params=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            class_name = (
                args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else None
            )
            func_name = f"{class_name}.{func.__name__}" if class_name else func.__name__
            logger = Logger(name="app", level=Logger.TRACE)
            logger.trace(f"Function {func_name} starts.")
            if trace_params:
                for param in trace_params:
                    if param.startswith("self.") and args:
                        attr = param.split(".", 1)[1]
                        traced_value = getattr(args[0], attr, None)
                        logger.trace(f"Function {func_name}: {param} = {traced_value}")
                    else:
                        traced_value = kwargs.get(param, None)
                        logger.trace(f"Function {func_name}: {param} = {traced_value}")
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.trace(
                f"Function {func_name} completed. Took {execution_time:.4f} seconds."
            )
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            class_name = (
                args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else None
            )
            func_name = f"{class_name}.{func.__name__}" if class_name else func.__name__
            logger = Logger(name="app", level=Logger.TRACE)
            logger.trace(f"Function {func_name} starts.")
            if trace_params:
                for param in trace_params:
                    if param.startswith("self.") and args:
                        attr = param.split(".", 1)[1]
                        traced_value = getattr(args[0], attr, None)
                        logger.trace(f"Function {func_name}: {param} = {traced_value}")
                    else:
                        traced_value = kwargs.get(param, None)
                        logger.trace(f"Function {func_name}: {param} = {traced_value}")
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.trace(
                f"Function {func_name} completed. Took {execution_time:.4f} seconds."
            )
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    if _func is None:
        return decorator
    else:
        return decorator(_func)