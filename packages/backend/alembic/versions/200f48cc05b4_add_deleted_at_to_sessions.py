"""add_deleted_at_to_sessions

Revision ID: 200f48cc05b4
Revises: b0f343f60519
Create Date: 2025-12-22 19:01:31.034555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '200f48cc05b4'
down_revision: Union[str, None] = 'b0f343f60519'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add deleted_at column for soft delete
    op.add_column('sessions', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    # Add index for deleted_at for filtering performance
    op.create_index('idx_sessions_deleted_at', 'sessions', ['deleted_at'])
    
    # Add composite index for user_id + started_at for better query performance
    op.create_index('idx_sessions_user_started_deleted', 'sessions', ['user_id', 'started_at', 'deleted_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_sessions_user_started_deleted', table_name='sessions')
    op.drop_index('idx_sessions_deleted_at', table_name='sessions')
    
    # Drop column
    op.drop_column('sessions', 'deleted_at')
