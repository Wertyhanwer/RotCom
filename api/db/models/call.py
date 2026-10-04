import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from db.models.base import Base


class CallStatus(enum.Enum):
    answered = "answered"
    missed = "missed"


class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("private_chats.id"), nullable=False)
    caller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(CallStatus), nullable=False)
    duration = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())