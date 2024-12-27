from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, ForeignKey
from services.database import Base


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # attachment_url: Mapped[str] = mapped_column(default=None, nullable=False) # url expires /:
    reaction_count: Mapped[int] = mapped_column(default=None, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False, default=None)
