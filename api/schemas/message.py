from typing import Literal
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MessageEvent(BaseModel):
    event_type: Literal["message"]
    to_user_id: int
    content: str
    content_type: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_type: Literal["message"] = "message"
    id_: int
    chat_id: int
    from_user_id: int
    content: str
    created_at: datetime


