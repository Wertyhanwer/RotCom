import uuid
from datetime import datetime, timedelta, timezone

import jwt

from .token_payload_model import TokenPayloadModel
from .token_settings import ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    """Возвращает (token, jti, expires_at в UTC без таймзоны — для записи в refresh_tokens)."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    payload = TokenPayloadModel(sub=str(user_id), type="refresh", exp=expire, jti=jti)
    token = jwt.encode(payload.model_dump(), SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expire.replace(tzinfo=None)
