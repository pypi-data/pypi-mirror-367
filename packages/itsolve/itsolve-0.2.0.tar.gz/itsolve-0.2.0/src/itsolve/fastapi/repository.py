from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models import Base

OrmModel = TypeVar("OrmModel", bound=Base)


class Repository[OrmModel]:
    TABLE: type[OrmModel]

    def __init__(
        self, async_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        self.async_session_factory = async_session_factory
