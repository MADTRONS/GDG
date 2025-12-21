"""merge_heads

Revision ID: bc9db1f7bb08
Revises: 7c20f740ea75, add_sessions_table
Create Date: 2025-12-21 15:08:17.882330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc9db1f7bb08'
down_revision: Union[str, None] = ('7c20f740ea75', 'add_sessions_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
