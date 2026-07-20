from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository.user_repository import UserRepository
from schemas.user import UserCreate, UserUpdateUsername, UserResponse
from dependencies import get_session_async
from dependencies.auth import get_current_user
from db.models.user import User
from .service import hash_password

import logging
logger = logging.getLogger("messenger.users")

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session_async)):
    logger.info(f"Create user request {{username: {data.username}, login: {data.login}}}")
    repo = UserRepository(session)
    password_hash = hash_password(data.password)
    user = await repo.create(data.username, data.email, password_hash)
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    logger.info(f"Get me request {{user_id: {current_user.id_}}}")
    return current_user


@router.get("/search", response_model=UserResponse)
async def search_user_by_login(
    login: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session_async),
):
    logger.info(f"Search user request {{login: {login}}}")
    repo = UserRepository(session)
    user = await repo.get_by_login(login)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session_async)):
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_username(user_id: int, data: UserUpdateUsername, session: AsyncSession = Depends(get_session_async)):
    repo = UserRepository(session)
    user = await repo.update_username_by_user_id(user_id, data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session_async)):
    repo = UserRepository(session)
    user = await repo.delete_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
