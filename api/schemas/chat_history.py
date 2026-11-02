from typing import Annotated, Union
from pydantic import Field, TypeAdapter

from schemas.message import MessageResponse
from schemas.call import CallResponse

# новый тип события: добавить его *Response сюда и *Event в schemas/ws_event.py
HistoryItem = Annotated[Union[MessageResponse, CallResponse], Field(discriminator="event_type")]

history_item_adapter = TypeAdapter(HistoryItem)
history_adapter = TypeAdapter(list[HistoryItem])
