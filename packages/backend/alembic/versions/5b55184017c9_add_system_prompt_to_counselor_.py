"""add_system_prompt_to_counselor_categories

Revision ID: 5b55184017c9
Revises: bc9db1f7bb08
Create Date: 2025-12-21 15:08:22.429637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b55184017c9'
down_revision: Union[str, None] = 'bc9db1f7bb08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('counselor_categories', sa.Column('system_prompt', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('counselor_categories', 'system_prompt')
