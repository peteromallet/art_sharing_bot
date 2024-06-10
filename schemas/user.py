import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column


class Base(MappedAsDataclass, AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    youtube: Mapped[Optional[str]] = mapped_column(default=None)
    twitter: Mapped[Optional[str]] = mapped_column(default=None)
    instagram: Mapped[Optional[str]] = mapped_column(default=None)
    website: Mapped[Optional[str]] = mapped_column(default=None)
    featured: Mapped[bool] = mapped_column(default=True)
    # created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
    # server_default=func.now()
    # )

    # def __init__(self):
    #     super().__init__()
