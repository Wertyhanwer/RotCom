from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, Text, func
from datetime import datetime
from .base import Base

class Message(Base):
    __tablename__ = "messages"

    id_: Mapped[int] = mapped_column("id",BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("private_chats.id"), nullable=False)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())