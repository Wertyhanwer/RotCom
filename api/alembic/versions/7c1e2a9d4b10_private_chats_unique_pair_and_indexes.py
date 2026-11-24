"""private_chats: unique user pair, ordering check and lookup indexes

Revision ID: 7c1e2a9d4b10
Revises: d65b3c391074
Create Date: 2026-11-24 15:00:00.000000

Без уникальности пары (user1_id, user2_id) одновременные первые сообщения двух
собеседников (или нескольких вкладок) создавали несколько чатов для одной пары.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7c1e2a9d4b10'
down_revision: Union[str, Sequence[str], None] = 'd65b3c391074'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    duplicates = op.get_bind().execute(sa.text(
        "SELECT user1_id, user2_id, array_agg(id ORDER BY id) AS ids FROM private_chats "
        "GROUP BY user1_id, user2_id HAVING count(*) > 1"
    )).all()
    if duplicates:
        # события этих чатов лежат в Mongo (chat_events.chat_id), поэтому автоматически
        # склеивать их здесь нельзя — нужно перенести события и удалить лишние чаты вручную
        details = "; ".join(f"users {row.user1_id}/{row.user2_id}: chats {list(row.ids)}" for row in duplicates)
        raise RuntimeError(f"Duplicate private chats must be merged before this migration: {details}")

    op.create_unique_constraint('uq_private_chats_users', 'private_chats', ['user1_id', 'user2_id'])
    # NOT VALID: правило действует для новых строк и не падает на старых данных,
    # где мог остаться чат пользователя с самим собой
    op.execute(
        'ALTER TABLE private_chats ADD CONSTRAINT ck_private_chats_user_order '
        'CHECK (user1_id < user2_id) NOT VALID'
    )
    # список чатов пользователя ищется по user1_id OR user2_id; user1_id покрыт уникальным индексом
    op.create_index('ix_private_chats_user2_id', 'private_chats', ['user2_id'])


def downgrade() -> None:
    op.drop_index('ix_private_chats_user2_id', table_name='private_chats')
    op.drop_constraint('ck_private_chats_user_order', 'private_chats', type_='check')
    op.drop_constraint('uq_private_chats_users', 'private_chats', type_='unique')
