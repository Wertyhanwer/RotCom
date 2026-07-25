from typing import Annotated, Union
from pydantic import Field

from schemas.message import MessageResponse
from schemas.call import CallResponse

HistoryItem = Annotated[Union[MessageResponse, CallResponse], Field(discriminator="event_type")]
