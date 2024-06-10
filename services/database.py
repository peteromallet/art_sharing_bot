from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_async_engine('sqlite+aiosqlite:///./database.db', echo=True)
sessionmaker = async_sessionmaker(autocommit=False, bind=engine)


def get_db_session() -> AsyncSession:
    return sessionmaker()
