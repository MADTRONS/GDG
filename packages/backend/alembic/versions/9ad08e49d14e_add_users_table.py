"""Add users table

Revision ID: 9ad08e49d14e
Revises: 
Create Date: 2025-12-20 13:04:44.430304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9ad08e49d14e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint(r"username ~ '^\\\[^\\\]+\\\[^\\\]+$'", name='username_format_check'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    
    # Create indexes
    op.create_index('idx_users_username', 'users', ['username'], unique=False)
    op.create_index('idx_users_is_blocked', 'users', ['is_blocked'], unique=False, postgresql_where=sa.text('is_blocked = true'))


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_users_is_blocked', table_name='users', postgresql_where=sa.text('is_blocked = true'))
    op.drop_index('idx_users_username', table_name='users')
    
    # Drop users table
    op.drop_table('users')
