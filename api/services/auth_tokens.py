import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository.refresh_token_repository import RefreshTokenRepository
from db.repository.user_repository import UserRepository
from routers.service.JWT.access_token_create import create_access_token
from routers.service.JWT.refresh_token_create import create_refresh_token
from routers.service.JWT.token_decode import decode_token
from routers.service.JWT.token_payload_model import TokenPayloadModel
from schemas.jwt_token import TokenResponse

logger = logging.getLogger("messenger.auth")


async def issue_token_pair(session: AsyncSession, user_id: int) -> TokenResponse:
    """Новая пара access + refresh; refresh регистрируется в таблице refresh_tokens."""
    refresh_token, jti, expires_at = create_refresh_token(user_id)
    await RefreshTokenRepository(session).create(jti, user_id, expires_at)
    await session.commit()
    return TokenResponse(access_token=create_access_token(user_id), refresh_token=refresh_token)


def decode_refresh_token(token: str) -> TokenPayloadModel:
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if payload.type != "refresh" or not payload.jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return payload


async def rotate_refresh_token(session: AsyncSession, token: str) -> TokenResponse:
    """Обмен refresh-токена на новую пару, старый токен отзывается (rotation).

    Если предъявлен уже отозванный токен, значит его использовали дважды — например, его
    украли и обменяли раньше владельца. Тогда отзываются все токены пользователя, и войти
    заново можно только по логину и паролю.
    """
    payload = decode_refresh_token(token)
    repo = RefreshTokenRepository(session)

    user_id = await repo.revoke_if_active(payload.jti)
    if user_id is None:
        existing = await repo.get(payload.jti)
        if existing is not None and existing.revoked_at is not None:
            logger.warning(f"Refresh token reuse detected, revoking all sessions {{user_id: {existing.user_id}}}")
            await repo.revoke_all_for_user(existing.user_id)
            await session.commit()
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or user.is_deleted:
        await session.commit()
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return await issue_token_pair(session, user_id)


async def revoke_refresh_token(session: AsyncSession, token: str):
    payload = decode_refresh_token(token)
    await RefreshTokenRepository(session).revoke_if_active(payload.jti)
    await session.commit()


async def revoke_all_user_tokens(session: AsyncSession, user_id: int):
    await RefreshTokenRepository(session).revoke_all_for_user(user_id)
    await session.commit()
