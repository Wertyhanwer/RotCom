from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, StringConstraints
from datetime import datetime

MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class MessageEvent(BaseModel):
    event_type: Literal["message"]
    to_user_id: int
    content: MessageText
    content_type: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_type: Literal["message"] = "message"
    id_: int
    chat_id: int
    from_user_id: int
    content: str
    created_at: datetime


