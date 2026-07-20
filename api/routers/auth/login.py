from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from email_validator import validate_email, EmailNotValidError

from dependencies import get_session_async
from schemas.jwt_token import TokenResponse
from routers.service.hash import verify_hash
from db.repository.user_repository import UserRepository
from db.models import User
from routers.service.JWT.access_token_create import create_access_token

router = APIRouter(prefix="/login", tags=["login"])

import logging
logger = logging.getLogger("messenger.auth")


@router.post("/", response_model=TokenResponse)
async def login_user(login: str, password: str, session: AsyncSession = Depends(get_session_async)):
    rep = UserRepository(session)
    if is_email(login):
        user = await rep.get_by_email(login)
        if user is None:
            logger.info(f"User does not exist by email: {login}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        user = await rep.get_by_login(login)
        if user is None:
            logger.info(f"User does not exist by login: {login}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

    if user is None:
        logger.info(f"User does not exist by login: {login}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not password_check(user, password):
        logger.info(f"Password does not match!: {login}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id_)
    return  TokenResponse(access_token=token)

def password_check(user: User, password: str) -> bool:
    return verify_hash(password_hash=user.password_hash, password=password)

def is_email(value: str) -> bool:
    try:
        validate_email(value, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False