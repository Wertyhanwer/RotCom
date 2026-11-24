"""add calls table

Revision ID: e4ebe0f795e2
Revises: f4395fc9935f
Create Date: 2026-07-25 15:50:27.845681

Пустая ревизия. Автогенерированный код здесь дословно повторял f4395fc9935f_init
(те же alter_column и внешние ключи) и падал при повторном применении. Сама таблица calls
создаётся в b3c4d5e6f7a8. Ревизия оставлена, чтобы не рвать цепочку down_revision у баз,
где она уже записана в alembic_version.
"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'e4ebe0f795e2'
down_revision: Union[str, Sequence[str], None] = 'f4395fc9935f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
