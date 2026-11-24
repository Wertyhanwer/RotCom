from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func
from .base import Base

class User(Base):
    __tablename__ = "users"

    id_: Mapped[int] = mapped_column("id", primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    # аккаунт удалён и анонимизирован (см. UserRepository.delete_user_by_id)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
