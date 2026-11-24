from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from email_validator import validate_email, EmailNotValidError

from dependencies import get_session_async
from schemas.jwt_token import TokenResponse
from routers.service.hash import verify_hash
from db.repository.user_repository import UserRepository
from db.models import User
from services.auth_tokens import issue_token_pair

router = APIRouter(prefix="/login", tags=["login"])

import logging
logger = logging.getLogger("messenger.auth")


@router.post("/", response_model=TokenResponse)
async def login_user(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session_async),
):
    # логин и пароль приходят в теле запроса (application/x-www-form-urlencoded, стандарт OAuth2),
    # а не в query-параметрах, которые попадают в URL, логи nginx и историю браузера.
    # Поле называется username по спецификации OAuth2, в него можно передать логин или email
    login, password = form.username, form.password
    rep = UserRepository(session)
    if is_email(login):
        user = await rep.get_by_email(login)
    else:
        user = await rep.get_by_login(login)

    if user is None:
        logger.info(f"User does not exist: {login}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not password_check(user, password):
        logger.info(f"Password does not match!: {login}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return await issue_token_pair(session, user.id_)

def password_check(user: User, password: str) -> bool:
    return verify_hash(password_hash=user.password_hash, password=password)

def is_email(value: str) -> bool:
    try:
        validate_email(value, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False