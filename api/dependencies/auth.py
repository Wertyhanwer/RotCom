from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session_async
from db.models.user import User
from db.repository.user_repository import UserRepository
from routers.service.JWT.token_decode import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),  # достаёт токен из заголовка
    session: AsyncSession = Depends(get_session_async)
) -> User:
    rep = UserRepository(session)
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(payload.sub)
    user = await rep.get_by_id(user_id)  # тянет юзера из БД
    if user is None:
        raise HTTPException(401)
    return user
