from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TokenPayloadModel(BaseModel):
    sub: str
    type: Literal["access", "refresh"]
    exp: datetime

