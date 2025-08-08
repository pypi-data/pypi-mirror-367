import logging
import os
from typing import Any

import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper("iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)


class Logger:
    _LOG_LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    def __init__(self, logger) -> None:
        self.logger = logger
        self.context: dict[str, Any] = {}
        self._log_level = self._get_log_level_from_env()

    def _get_log_level_from_env(self) -> int:
        env_level = os.getenv("pyla_logger_level", "debug").lower()
        return self._LOG_LEVELS.get(env_level, logging.DEBUG)

    def _should_log(self, level: int) -> bool:
        return level >= self._log_level

    def add_context(self, **new_values: Any):
        self.context.update(new_values)

    def debug(self, event: str | None = None, *args: Any, **kw: Any) -> None:
        if not self._should_log(logging.DEBUG):
            return
        self._combine_with_context(kw)
        self.logger.debug(event, *args, **kw)

    def info(self, event: str | None = None, *args: Any, **kw: Any) -> None:
        if not self._should_log(logging.INFO):
            return
        self._combine_with_context(kw)
        self.logger.info(event, *args, **kw)

    def warning(self, event: str | None = None, *args: Any, **kw: Any) -> None:
        if not self._should_log(logging.WARNING):
            return
        self._combine_with_context(kw)
        self.logger.warning(event, *args, **kw)

    def error(self, event: str | None = None, *args: Any, **kw: Any) -> None:
        if not self._should_log(logging.ERROR):
            return
        self._combine_with_context(kw)
        self.logger.error(event, *args, **kw)

    def critical(self, event: str | None = None, *args: Any, **kw: Any) -> None:
        if not self._should_log(logging.CRITICAL):
            return
        self._combine_with_context(kw)
        self.logger.critical(event, *args, **kw)

    def exception(self, exc: Exception, event: str | None = None, *args: Any, **kw: Any) -> None:
        if not self._should_log(logging.ERROR):
            return
        self._combine_with_context(kw)
        self.logger.exception(event, *args, exc_info=exc, **kw)

    def _combine_with_context(self, values: dict[str, Any]):
        values.update(self.context)
        return values.update(self.context)


logger = Logger(structlog.get_logger())
