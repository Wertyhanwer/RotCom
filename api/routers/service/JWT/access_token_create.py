from datetime import datetime, timedelta, timezone

import jwt
from .token_settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .token_payload_model import TokenPayloadModel

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = TokenPayloadModel(
        sub=str(user_id),
        type="access",
        exp=expire,
    )

    token = jwt.encode(payload.model_dump(), SECRET_KEY, algorithm=ALGORITHM)
    return token