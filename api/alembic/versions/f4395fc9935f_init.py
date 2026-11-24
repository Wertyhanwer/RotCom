"""init

Revision ID: f4395fc9935f
Revises:
Create Date: 2026-07-08 00:54:10.385290

Базовая схема Postgres (users, private_chats). Раньше эта миграция только меняла таблицы,
созданные SQL-скриптами db/init, и на пустой базе падала. Теперь alembic — единственный
источник схемы, поэтому миграция создаёт таблицы сама. Проверки через inspector нужны для
баз, которые уже были созданы старыми init-скриптами без alembic_version: там таблицы есть,
и миграция только догоняет их до нужного вида (колонка last_message, внешние ключи).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f4395fc9935f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()

    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('username', sa.String(255), nullable=False),
            sa.Column('login', sa.String(255), nullable=False, unique=True),
            sa.Column('email', sa.String(255), nullable=False, unique=True),
            sa.Column('password_hash', sa.String(255), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        )
    else:
        op.alter_column('users', 'created_at', existing_type=sa.TIMESTAMP(), nullable=False,
                        existing_server_default=sa.text('now()'))

    if 'private_chats' not in tables:
        op.create_table(
            'private_chats',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user1_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('user2_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
            sa.Column('last_event_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
            sa.Column('last_message', sa.Text(), nullable=True),
        )
        return

    columns = {column['name'] for column in inspector.get_columns('private_chats')}
    if 'last_message' not in columns:
        op.add_column('private_chats', sa.Column('last_message', sa.Text(), nullable=True))
    for column in ('created_at', 'last_event_at'):
        op.alter_column('private_chats', column, existing_type=sa.TIMESTAMP(), nullable=False,
                        existing_server_default=sa.text('now()'))

    fk_columns = {tuple(fk['constrained_columns']) for fk in inspector.get_foreign_keys('private_chats')}
    for column in ('user1_id', 'user2_id'):
        if (column,) not in fk_columns:
            op.create_foreign_key(f'private_chats_{column}_fkey', 'private_chats', 'users', [column], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP TABLE IF EXISTS calls')
    op.execute('DROP TABLE IF EXISTS messages')
    op.drop_table('private_chats')
    op.drop_table('users')
