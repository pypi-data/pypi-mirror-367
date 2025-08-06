# mypy: disable-error-code="unused-ignore"
from typing import Callable, Iterable, TypedDict, TypeVar

from pydantic import BaseModel, create_model

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class Params(TypedDict):
    name_prefix: str | None


def omit_model_fields(
    model: type[BaseModelT], *fields_to_omit: Iterable[str], config: Params
) -> type[BaseModelT]:
    filtered_fields = {
        field_name: field
        for field_name, field in model.model_fields.items()
        if field_name not in fields_to_omit
    }
    fields = {
        field_name: (
            field_info.annotation,
            field_info,
        )
        for field_name, field_info in filtered_fields.items()
    }
    return create_model(  # type: ignore
        f"{config['name_prefix']}{model.__name__}",
        __module__=model.__module__,
        __doc__=model.__doc__,
        **fields,  # type: ignore
    )


def omit(
    *fields_to_omit: Iterable[str], name_prefix: str = ""
) -> Callable[[type[BaseModelT]], type[BaseModelT]]:
    def wrapper(cls: type[BaseModelT]) -> type[BaseModelT]:
        return omit_model_fields(
            cls, *fields_to_omit, config=Params(name_prefix=name_prefix)
        )

    return wrapper
