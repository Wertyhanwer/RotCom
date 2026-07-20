from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class OtherUserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_: int
    username: str
    login: str


class PrivateChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_: int
    created_at: datetime
    last_event_at: datetime
    last_message: Optional[str]
    other_user: OtherUserInfo
