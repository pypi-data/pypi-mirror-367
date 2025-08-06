from __future__ import annotations

from pprint import pformat
from typing import TYPE_CHECKING, Any, Callable

from pydantic import BaseModel

from settings import get_settings

if TYPE_CHECKING:
    from loguru import Record

settings = get_settings()


# TODO: Replace with ORM model
class UserMock(BaseModel):
    name: str
    age: int
    id: int | None = None


Anonymous = UserMock(name="Anonymous", age=0, id=None)


def formatter(time_format: str) -> Callable[[Record], Any]:
    def format_function(record: Record) -> str:
        time = "<green>{time:" + time_format + "}</green> | "
        def_format = (
            time + "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> "
            "<magenta>[{extra[logger_name]}]</magenta>"
            # "<blue>context: {extra}</blue>"
        )
        if settings.observability.enabled:
            def_format += (
                " [<red>trace_id={extra[otelTraceID]} "
                + "span_id={extra[otelSpanID]} "
                + "resource.service.name={extra[otelServiceName]}</red>]"
            )

        def_format += " - <level>{message}</level>{exception}"
        ctx = record["extra"].get("ctx", None)
        user: UserMock | None = record["extra"].get("user", None)
        if not ctx and not user:
            return def_format + "\n"
        level = record["level"].name
        record["extra"]["ctx"] = pformat(
            ctx,
            width=settings.logger.ctx_width,
            indent=settings.logger.ctx_indent,
            underscore_numbers=settings.logger.ctx_underscore_numbers,
            compact=settings.logger.ctx_compact,
            depth=None if level == "DEBUG" else settings.logger.ctx_depth,
        )
        return_formate = def_format
        if user:
            user_format = (
                f"<yellow>User: {user.name} - {user.id}</yellow>"
                if user.id
                else "Anonymous"
            )
            return_formate += f" ({user_format})"
        context_format = "<green>{extra[ctx]}</green>"
        # exeption_format = "<red>{exception}</red>" TODO: Add exception
        if ctx:
            return_formate += "\n" + context_format
        return return_formate + "\n"

    return format_function
