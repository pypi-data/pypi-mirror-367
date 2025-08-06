from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from models import Base

OrmModel = TypeVar("OrmModel", bound=Base)
ID = TypeVar("ID")
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class ICreateMixin[OrmModel, CreateSchema](Protocol):
    """
    Provide `create` method

    Example:
        ```python
        class IYourRepo(ICreateMixin[YourOrm, YourCreateSchema]):
        ```

    Generic:
        `OrmModel`: Orm model

        `CreateSchema`: Pydantic model

    Args:
        `data`: Pydantic model

    Returns:
        Orm model
    """

    async def create(self, data: CreateSchema) -> OrmModel: ...


class IRetrieveMixin[OrmModel, ID](Protocol):
    """
    Provide `retrieve` and `retrieve_by` methods

    Example:
        ```python
        class IYourRepo(IRetrieveMixin[YourOrm, int]):
        ```

    Generics:
        `OrmModel`: Orm model

        `ID`: Primary key type

    Args:
        `retrieve` - `id`: Primary key

        `retrieve_by` - `**filters`: Filters
    Returns:
        Orm model
    """

    async def retrieve(self, id: ID) -> OrmModel: ...

    async def retrieve_by(self, **filters: dict[str, Any]) -> OrmModel: ...


class IUpdateMixin[OrmModel, ID, UpdateSchema](Protocol):
    """
    Provide `update` method

    Example:
        ```python
        class IYourRepo(IUpdateMixin[YourOrm, int, YourUpdateSchema]):
        ```

    Generics:
        `OrmModel`: Orm model

        `UpdateSchema`: Pydantic model

        `ID`: Primary key

    Args:
        `id`: Primary key

        `data`: Pydantic model

    Returns:
        Orm model
    """

    async def update(self, id: ID, data: UpdateSchema) -> OrmModel: ...


class IDeleteMixin[ID](Protocol):
    """
    Provide `delete` method

    Example:
        ```python
        class IYourRepo(IDeleteMixin[int]):
        ```

    Generics:
        `ID`: Primary key

    Args:
        `id`: Primary key

    Returns:
        Primary key
    """

    async def delete(self, id: ID) -> ID: ...


class FilterMixin[OrmModel](Protocol):
    """
    Provide `filter` method

    Example:
        ```python
        class IYourRepo(FilterMixin[YourOrm]):
        ```

    Generics:
        `OrmModel`: Orm model

    Args:
        `**filters`: Filters

    Returns:
        List of Orm models
    """

    async def filter(self, **filters: dict[str, Any]) -> list[OrmModel]: ...


class IReadableMixin[OrmModel, ID](IRetrieveMixin[OrmModel, ID]):
    """
    Provide `retrieve` and `retrieve_by` methods

    Example:
        ```python
        class IYourRepo(IReadableMixin[YourOrm, int]):
        ```

    Generics:
        `OrmModel`: Orm model

        `ID`: Primary key type

    Args:
        `retrieve` - `id`: Primary key

        `retrieve_by` - `**filters`: Filters

    Returns:
        Orm model
    """


class IWritableMixin[OrmModel, ID, CreateSchema, UpdateSchema](
    ICreateMixin[OrmModel, CreateSchema],
    IUpdateMixin[OrmModel, ID, UpdateSchema],
):
    """
    Provide `create` and `update` methods

    Example:
        ```python
        class IYourRepo(
            IWritableMixin[
                YourOrm,
                int,
                YourCreateSchema,
                YourUpdateSchema
            ]
        ):
        ```

    Generics:
        `OrmModel`: Orm model

        `ID`: Primary key

        `CreateSchema`: Pydantic model

        `UpdateSchema`: Pydantic model

    Args:
        `create` - `data`: Pydantic model

        `update` - `id`: Primary key, `data`: Pydantic model

    Returns:
        Orm model
    """


class ICRUDMixin[OrmModel, ID, CreateSchema, UpdateSchema](
    ICreateMixin[OrmModel, CreateSchema],
    IRetrieveMixin[OrmModel, ID],
    IUpdateMixin[OrmModel, ID, UpdateSchema],
    IDeleteMixin[ID],
):
    """
    Provide `create`, `retrieve`, `update` and `delete` methods

    Example:
        ```python
        class IYourRepo(
            ICRUDMixin[YourOrm, int, YourCreateSchema, YourUpdateSchema]
        ):
        ```

    Generics:
        `OrmModel`: Orm model

        `ID`: Primary key

        `CreateSchema`: Pydantic model

        `UpdateSchema`: Pydantic model

    Args:
        `create` - `data`: Pydantic model

        `retrieve` - `id`: Primary key

        `retrieve_by` - `**filters`: Filters

        `update` - `id`: Primary key, `data`: Pydantic model

        `delete` - `id`: Primary key

    Returns:
        Orm model
    """
