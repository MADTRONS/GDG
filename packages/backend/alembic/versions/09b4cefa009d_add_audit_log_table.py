"""add_audit_log_table

Revision ID: 09b4cefa009d
Revises: 4c0471d51f51
Create Date: 2025-12-22 22:29:37.008176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '09b4cefa009d'
down_revision: Union[str, None] = '4c0471d51f51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create AuditAction enum type
    audit_action_enum = postgresql.ENUM(
        'CREATE',
        'UPDATE',
        'DELETE',
        'LOGIN',
        'LOGOUT',
        name='auditaction',
        create_type=False
    )
    audit_action_enum.create(op.get_bind(), checkfirst=True)
    
    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('admin_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', audit_action_enum, nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_audit_log_admin_user_id', 'audit_log', ['admin_user_id'], unique=False)
    op.create_index('idx_audit_log_timestamp', 'audit_log', ['timestamp'], unique=False)
    op.create_index('idx_audit_log_resource', 'audit_log', ['resource_type', 'resource_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_audit_log_resource', table_name='audit_log')
    op.drop_index('idx_audit_log_timestamp', table_name='audit_log')
    op.drop_index('idx_audit_log_admin_user_id', table_name='audit_log')
    
    # Drop table
    op.drop_table('audit_log')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS auditaction')

