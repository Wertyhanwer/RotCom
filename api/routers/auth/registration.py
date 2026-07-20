from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from routers.auth.exceptions import RegistrationError
from routers.service import hash_password
from schemas.user import UserResponse, UserCreate
from db.repository.user_repository import UserRepository
from dependencies import get_session_async
from .exceptions import UserAlreadyExistsError


import logging
logger = logging.getLogger("messenger.auth")

router = APIRouter(prefix="/registration", tags=["registration"])

@router.post("/", response_model=UserResponse)
async def register_user(data: UserCreate, session: AsyncSession = Depends(get_session_async)):
    rep = UserRepository(session)
    if await rep.get_by_email(data.email) is not None:
        logger.error(f"User already exists with email {data.email}!")
        raise HTTPException(status_code=409, detail="User with this email already exists")

    if await rep.get_by_login(data.login) is not None:
        logger.error(f"User already exists with login {data.login}!")
        raise HTTPException(status_code=409, detail="User with this login already exists")

    try:
        _password = hash_password(data.password)
        new_user = await rep.create(data.username, data.login, data.email, _password)
    except Exception as e:
        logger.critical(f"Something went wrong... {e}")
        raise RegistrationError(f"Something went wrong... {e}")

    return new_user
