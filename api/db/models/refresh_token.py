from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RefreshToken(Base):
    """Выданный refresh-токен. Сам токен — JWT, здесь хранится только его jti и статус."""
    __tablename__ = "refresh_tokens"

    jti: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
