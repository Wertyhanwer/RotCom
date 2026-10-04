from typing import Annotated, Union
from pydantic import Field

from schemas.message import MessageEvent
from schemas.call import CallEvent

WsEvent = Annotated[Union[MessageEvent, CallEvent], Field(discriminator="event_type")]
