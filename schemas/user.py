from sqlalchemy import func
from schemas.post import Post
from typing import List
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(default=None,  nullable=False)
    youtube: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    twitter: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    instagram: Mapped[Optional[str]] = mapped_column(
        default=None, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    featured: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[Optional[datetime]
                       ] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]
                       ] = mapped_column(default=func.now(), server_onupdate=func.now())
    posts: Mapped[List["Post"]] = relationship(
        backref="post", default_factory=list, lazy="joined")

# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
# https://www.youtube.com/watch?v=wvQJzMrKy9E
# https://stackoverflow.com/questions/74252768/missinggreenlet-greenlet-spawn-has-not-been-called
