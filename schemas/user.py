from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from services.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    youtube: Mapped[Optional[str]] = mapped_column(default=None)
    twitter: Mapped[Optional[str]] = mapped_column(default=None)
    instagram: Mapped[Optional[str]] = mapped_column(default=None)
    website: Mapped[Optional[str]] = mapped_column(default=None)
    featured: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[Optional[datetime]
                       ] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]
                       ] = mapped_column(default=func.now(), server_onupdate=func.now())
