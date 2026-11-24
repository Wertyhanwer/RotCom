from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session_async
from schemas.jwt_token import RefreshRequest, TokenResponse
from services.auth_tokens import revoke_refresh_token, rotate_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, session: AsyncSession = Depends(get_session_async)):
    """Новая пара токенов в обмен на refresh-токен; старый refresh-токен больше не действует."""
    return await rotate_refresh_token(session, data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(data: RefreshRequest, session: AsyncSession = Depends(get_session_async)):
    """Отзывает refresh-токен. Access-токен короткоживущий (30 минут) и истечёт сам."""
    await revoke_refresh_token(session, data.refresh_token)
    return Response(status_code=204)
