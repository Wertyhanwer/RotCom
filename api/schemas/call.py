from pydantic import BaseModel, ConfigDict
from datetime import datetime

from db.models.call import CallStatus


class CallIn(BaseModel):
    status: CallStatus
    duration: int


class CallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_: int
    chat_id: int
    caller_id: int
    status: CallStatus
    duration: int
    created_at: datetime
