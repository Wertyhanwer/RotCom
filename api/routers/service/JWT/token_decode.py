import jwt

from .token_settings import SECRET_KEY, ALGORITHM
from .token_payload_model import TokenPayloadModel

def decode_token(token: str) -> TokenPayloadModel:
    raw_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return TokenPayloadModel.model_validate(raw_payload)