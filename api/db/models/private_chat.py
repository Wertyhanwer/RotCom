from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, ForeignKey, Text
from .base import Base

class PrivateChat(Base):
    __tablename__ = "private_chats"

    id_: Mapped[int] = mapped_column("id", primary_key=True)
    user1_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user2_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    last_event_at: Mapped[datetime] = mapped_column(default=func.now())
    last_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
