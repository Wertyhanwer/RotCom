"""create calls table

Revision ID: b3c4d5e6f7a8
Revises: e4ebe0f795e2
Create Date: 2026-07-25 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'e4ebe0f795e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'calls',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chat_id', sa.Integer(), sa.ForeignKey('private_chats.id'), nullable=False),
        sa.Column('caller_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.Enum('answered', 'missed', name='callstatus'), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('calls')
    op.execute('DROP TYPE IF EXISTS callstatus')
