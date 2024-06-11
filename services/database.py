from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase, AsyncAttrs):
    pass


engine = create_async_engine('sqlite+aiosqlite:///./database.db', echo=True)

sessionmaker = async_sessionmaker(autocommit=False, bind=engine)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db_session() -> AsyncSession:
    return sessionmaker()
