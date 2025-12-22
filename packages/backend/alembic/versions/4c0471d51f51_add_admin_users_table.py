"""add_admin_users_table

Revision ID: 4c0471d51f51
Revises: 672c05922909
Create Date: 2025-12-22 21:23:40.728230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4c0471d51f51'
down_revision: Union[str, None] = '672c05922909'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create AdminRole enum type (with checkfirst to handle re-runs)
    admin_role_enum = postgresql.ENUM(
        'SUPER_ADMIN',
        'SYSTEM_MONITOR',
        'CONTENT_MANAGER',
        name='adminrole',
        create_type=False  # Don't auto-create from table
    )
    admin_role_enum.create(op.get_bind(), checkfirst=True)

    # Create admin_users table
    op.create_table(
        'admin_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', admin_role_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_admin_users_email', 'admin_users', ['email'], unique=True)
    op.create_index('ix_admin_users_is_active', 'admin_users', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_admin_users_is_active', table_name='admin_users')
    op.drop_index('ix_admin_users_email', table_name='admin_users')
    
    # Drop table
    op.drop_table('admin_users')
    
    # Drop enum type
    admin_role_enum = postgresql.ENUM(
        'SUPER_ADMIN',
        'SYSTEM_MONITOR',
        'CONTENT_MANAGER',
        name='adminrole'
    )
    admin_role_enum.drop(op.get_bind(), checkfirst=True)
