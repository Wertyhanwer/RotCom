import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.exceptions import DatabaseError
from db.models.refresh_token import RefreshToken


def _utcnow() -> datetime:
    # колонки TIMESTAMP без таймзоны, храним UTC
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RefreshTokenRepository:
    """Методы не коммитят — транзакцией управляет services/auth_tokens.py."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger("messenger.db")

    async def create(self, jti: str, user_id: int, expires_at: datetime):
        try:
            self._session.add(RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at))
            await self._session.flush()
        except Exception as e:
            self._logger.error(f"Error at creating refresh token {{user_id: {user_id}}}: {e}")
            raise DatabaseError(f"Error at creating refresh token {{user_id: {user_id}}}") from e

    async def get(self, jti: str) -> RefreshToken | None:
        result = await self._session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        return result.scalar_one_or_none()

    async def revoke_if_active(self, jti: str) -> int | None:
        """Атомарно отзывает действующий токен и возвращает его user_id; None — если токен
        не найден, уже отозван или истёк. Это один UPDATE ... WHERE revoked_at IS NULL, поэтому из
        двух одновременных обменов одного и того же токена успешным будет только один."""
        result = await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.jti == jti,
                   RefreshToken.revoked_at.is_(None),
                   RefreshToken.expires_at > _utcnow())
            .values(revoked_at=_utcnow())
            .returning(RefreshToken.user_id)
        )
        return result.scalar_one_or_none()

    async def revoke_all_for_user(self, user_id: int):
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=_utcnow())
        )
