from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TokenPayloadModel(BaseModel):
    sub: str
    type: Literal["access", "refresh"]
    exp: datetime
    # идентификатор refresh-токена в таблице refresh_tokens (у access-токена отсутствует)
    jti: str | None = None

