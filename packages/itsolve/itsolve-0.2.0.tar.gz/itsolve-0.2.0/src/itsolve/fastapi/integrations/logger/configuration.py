from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import TYPE_CHECKING, cast

from loguru import logger
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter
from loki_logger_handler.loki_logger_handler import (
    LoggerFormatter,
    LokiLoggerHandler,
)
from opentelemetry.trace import (
    INVALID_SPAN,
    INVALID_SPAN_CONTEXT,
    get_current_span,
    get_tracer_provider,
)

from settings import get_settings

from .formatter import formatter

if TYPE_CHECKING:
    from loguru import Record

settings = get_settings()


def console_logger_configure() -> None:
    logger.add(
        sys.stdout,
        format=formatter(settings.logger.console_time_format),
        colorize=True,
        level=settings.logger.console_level,
        diagnose=settings.MODE != "prod",
    )


def file_logger_configure() -> None:
    logger.add(
        f"{settings.logger.file_dir}/{settings.logger.file_name}",
        format=formatter(settings.logger.file_time_format),
        rotation=settings.logger.file_rotation,
        level=settings.logger.file_level,
        compression=settings.logger.file_compression,
        colorize=False,
        diagnose=settings.MODE != "prod",
    )


def instrument_loguru() -> None:
    provider = get_tracer_provider()
    service_name = None

    def add_trace_context(record: Record) -> None:
        record["extra"]["otelSpanID"] = "0"
        record["extra"]["otelTraceID"] = "0"
        record["extra"]["otelTraceSampled"] = False
        record["extra"]["asctime"] = datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        nonlocal service_name
        if service_name is None:
            resource = getattr(provider, "resource", None)
            if resource:
                service_name = resource.attributes.get("service.name") or ""
            else:
                service_name = ""

        record["extra"]["otelServiceName"] = service_name

        span = get_current_span()
        if span != INVALID_SPAN:
            ctx = span.get_span_context()
            if ctx != INVALID_SPAN_CONTEXT:
                record["extra"]["otelSpanID"] = format(ctx.span_id, "016x")
                record["extra"]["otelTraceID"] = format(ctx.trace_id, "032x")
                record["extra"]["otelTraceSampled"] = ctx.trace_flags.sampled

    logger.configure(patcher=add_trace_context)


def configure_logger() -> None:
    logger.remove()
    logger.opt(lazy=True, record=True, depth=1)
    logger.configure(extra={"logger_name": settings.project.name})
    if settings.logger.console:
        console_logger_configure()
    if settings.logger.file:
        file_logger_configure()
    configure_uvicorn_logging()
    if settings.observability.enabled:
        instrument_loguru()
        logger.configure(extra={"otelSpanID": 0, "otelTraceID": 0})

        custom_handler = LokiLoggerHandler(
            url="http://localhost:3100/loki/api/v1/push",
            labels={
                "application": settings.project.name,
                "environment": settings.MODE,
            },
            label_keys={},
            timeout=10,
            default_formatter=cast(LoggerFormatter, LoguruFormatter()),
        )
        logger.add(custom_handler, serialize=True)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Получаем соответствующий уровень Loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore

        exception = None
        depth = 2
        if record.exc_info:
            exception = record.exc_info[1]
            depth = 6

        # Сохраняем оригинальный стектрейс
        frame = logging.currentframe()
        while frame.f_code.co_filename == logging.__file__:  # type: ignore[unused-ignore]
            frame = frame.f_back  # type: ignore
        message = record.getMessage().replace("{", "{{").replace("}", "}}")
        logger.opt(
            depth=depth, exception=exception, record=True, lazy=True
        ).bind(logger_name=record.name).log(level, message)


def configure_uvicorn_logging() -> None:
    # Перехватываем логи Uvicorn
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Отключаем стандартные обработчики Uvicorn
    for name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy.engine.Engine",
    ]:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
