"""move messages and calls to mongo

Revision ID: d65b3c391074
Revises: b3c4d5e6f7a8
Create Date: 2026-11-02 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd65b3c391074'
down_revision: Union[str, Sequence[str], None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # сообщения и звонки теперь в Mongo (коллекция chat_events). IF EXISTS — в разных окружениях
    # таблицы создавались то init-скриптами, то миграциями, и могут отсутствовать
    op.execute('DROP TABLE IF EXISTS calls')
    op.execute('DROP TABLE IF EXISTS messages')
    op.execute('DROP TYPE IF EXISTS callstatus')
    op.execute('DROP TYPE IF EXISTS call_status')


def downgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('chat_id', sa.Integer(), sa.ForeignKey('private_chats.id'), nullable=False),
        sa.Column('from_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    )
    op.create_table(
        'calls',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chat_id', sa.Integer(), sa.ForeignKey('private_chats.id'), nullable=False),
        sa.Column('caller_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.Enum('answered', 'missed', name='callstatus'), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    )
