import enum
from typing import Literal
from pydantic import Field, NonNegativeInt

from schemas.chat_event import BaseEvent, BaseEventResponse


class CallStatus(enum.Enum):
    answered = "answered"
    missed = "missed"


class CallEvent(BaseEvent):
    event_type: Literal["call"]
    status: CallStatus
    duration: NonNegativeInt

    def preview(self) -> str:
        return "📞 Звонок" if self.status == CallStatus.answered else "📵 Пропущенный звонок"


class CallResponse(BaseEventResponse):
    event_type: Literal["call"] = "call"
    caller_id: int = Field(validation_alias="sender_id")
    status: CallStatus
    duration: int
