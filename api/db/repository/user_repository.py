import logging

from db.exceptions import DatabaseError
from db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logging.getLogger("messenger.db")

    async def create(self, username: str, login: str, email: str, password_hash: str) -> User:
        self._logger.info(f"User create request {{username: {username}, login: {login}, email: {email}}}")
        try:
            user = User(username=username, login=login, email=email, password_hash=password_hash)
            self._session.add(user)
            await self._session.commit()
            await self._session.refresh(user)
            return user
        except Exception as e:
            self._logger.error(f"Error at user creating {username}: {e}")
            raise DatabaseError(f"Error at user creating {username}") from e

    async def get_by_id(self, user_id: int) -> User | None:
        self._logger.info(f"Get user by id request {{id: {user_id} }}")
        try:
            result = await self._session.execute(
                select(User).where(User.id_ == user_id)
            )
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            self._logger.error(f"Error at user getting user by id {user_id}: {e}")
            raise DatabaseError(f"Error at user getting user by id {user_id}.") from e

    async def get_by_email(self, user_email: str) -> User | None:
        self._logger.info(f"Get user by email request {{email: {user_email} }}")
        try:
            result = await self._session.execute(
                select(User).where(User.email == user_email)
            )
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            self._logger.error(f"Error at user getting user by email {user_email}: {e}")
            raise DatabaseError(f"Error at user getting user by email {user_email}.") from e

    async def get_by_login(self, login: str) -> User | None:
        self._logger.info(f"Get user by login request {{login: {login} }}")
        try:
            result = await self._session.execute(
                select(User).where(User.login == login)
            )
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            self._logger.error(f"Error at user getting user by login {login}: {e}")
            raise DatabaseError(f"Error at user getting user by login {login}.") from e

    async def update_username_by_user_id(self, user_id: int, new_username: str) -> User | None:
        self._logger.info(f"Update user.name by id request {{id: {user_id}, username: {new_username} }}")
        try:
            user: User = await self.get_by_id(user_id)
            if user is None:
               return None

            user.username = new_username
            await self._session.commit()
            await self._session.refresh(user)
            return user
        except Exception as e:
            self._logger.error(f"Error at update user.name by id {{id: {user_id}, username: {new_username}  {user_id}: {e} }}")
            raise DatabaseError(f"Error at update user.name by id {{id: {user_id}, username: {new_username}  {user_id}: {e} }}") from e

    async def delete_user_by_id(self, user_id: int) -> User | None:
        self._logger.info(f"Delete user by id request {{id: {user_id}}}")
        try:
            user: User = await self.get_by_id(user_id)
            if user is None:
                return None
            await self._session.delete(user)
            await self._session.commit()
            return user
        except Exception as e:
            self._logger.error(f"Error at delete user by id {user_id}: {e}")
            raise DatabaseError(f"Error at delete user by id {user_id}: {e}") from e