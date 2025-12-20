"""fix_username_format_constraint

Revision ID: df870ce3dc0f
Revises: 9ad08e49d14e
Create Date: 2025-12-20 21:28:47.415408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df870ce3dc0f'
down_revision: Union[str, None] = '9ad08e49d14e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old constraint
    op.drop_constraint('username_format_check', 'users', type_='check')
    
    # Add the correct constraint that matches \domain\username format
    op.create_check_constraint(
        'username_format_check',
        'users',
        r"username ~ '^\\[^\\]+\\[^\\]+$'"
    )


def downgrade() -> None:
    # Drop the new constraint
    op.drop_constraint('username_format_check', 'users', type_='check')
    
    # Restore the old constraint
    op.create_check_constraint(
        'username_format_check',
        'users',
        r"username ~ '^\\\[^\\\]+\\\[^\\\]+$'"
    )
