# mypy: disable-error-code="unused-ignore"
from copy import deepcopy
from typing import Any, Callable, TypedDict, TypeVar

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefinedType


def make_field_optional(
    field: FieldInfo, default: Any = None
) -> tuple[Any, FieldInfo]:
    new = deepcopy(field)
    if not isinstance(field.default, PydanticUndefinedType):
        new.default = field.default
    else:
        new.default = default
    new.annotation = field.annotation | None  # type: ignore
    return (new.annotation, new)


BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class Params(TypedDict):
    name_prefix: str | None


def make_partial_model(
    model: type[BaseModelT], config: Params
) -> type[BaseModelT]:
    return create_model(  # type: ignore
        f"{config.get('name_prefix')}{model.__name__}",
        __module__=model.__module__,
        __doc__=model.__doc__,
        __base__=model.__base__,  # type: ignore
        **{
            field_name: make_field_optional(field_info)  # type: ignore
            for field_name, field_info in model.model_fields.items()
        },
    )


def make_partial(
    *,
    name_prefix: str = "",
) -> Callable[[type[BaseModelT]], type[BaseModelT]]:
    def wrapper(cls: type[BaseModelT]) -> type[BaseModelT]:
        return make_partial_model(cls, Params(name_prefix=name_prefix))

    return wrapper
