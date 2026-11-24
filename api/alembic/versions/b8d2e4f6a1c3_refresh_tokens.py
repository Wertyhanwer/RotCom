"""refresh_tokens: server-side registry of issued refresh tokens

Revision ID: b8d2e4f6a1c3
Revises: 9a3f5c2b7d41
Create Date: 2026-11-24 18:00:00.000000

Refresh-токен — JWT с jti; запись в этой таблице позволяет отозвать его (logout, удаление
аккаунта) и обнаружить повторное использование уже обменянного токена.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8d2e4f6a1c3'
down_revision: Union[str, Sequence[str], None] = '9a3f5c2b7d41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'refresh_tokens',
        sa.Column('jti', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('revoked_at', sa.TIMESTAMP(), nullable=True),
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
