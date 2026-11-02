from typing import Annotated, Literal
from pydantic import Field, StringConstraints

from schemas.chat_event import BaseEvent, BaseEventResponse

MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class MessageEvent(BaseEvent):
    event_type: Literal["message"]
    content: MessageText

    def preview(self) -> str:
        return self.content


class MessageResponse(BaseEventResponse):
    event_type: Literal["message"] = "message"
    from_user_id: int = Field(validation_alias="sender_id")
    content: str
