"""users.deleted_at for account deletion via anonymization

Revision ID: 9a3f5c2b7d41
Revises: 7c1e2a9d4b10
Create Date: 2026-11-24 17:00:00.000000

Физически удалить пользователя с чатами нельзя (на него ссылается private_chats), а удаление
его чатов стёрло бы историю у собеседников. Поэтому аккаунт анонимизируется, а момент
удаления хранится в deleted_at.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9a3f5c2b7d41'
down_revision: Union[str, Sequence[str], None] = '7c1e2a9d4b10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'deleted_at')
