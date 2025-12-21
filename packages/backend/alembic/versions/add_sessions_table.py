"""Add sessions table for voice/video tracking

Revision ID: add_sessions_table
Revises: 
Create Date: 2025-12-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = ''add_sessions_table''
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sessions table
    op.create_table(''sessions'',
        sa.Column(''id'', postgresql.UUID(as_uuid=True), server_default=sa.text(''gen_random_uuid()''), nullable=False),
        sa.Column(''user_id'', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(''counselor_category'', sa.String(length=100), nullable=False),
        sa.Column(''mode'', sa.String(length=20), nullable=False),
        sa.Column(''room_name'', sa.String(length=100), nullable=False),
        sa.Column(''transcript'', sa.Text(), nullable=True),
        sa.Column(''duration_seconds'', sa.Integer(), nullable=True),
        sa.Column(''started_at'', sa.DateTime(), server_default=sa.text(''CURRENT_TIMESTAMP''), nullable=False),
        sa.Column(''ended_at'', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint([''user_id''], [''users.id''], ondelete=''CASCADE''),
        sa.PrimaryKeyConstraint(''id''),
        sa.UniqueConstraint(''room_name'')
    )
    
    # Create indexes
    op.create_index(''idx_sessions_category'', ''sessions'', [''counselor_category''])
    op.create_index(''idx_sessions_mode'', ''sessions'', [''mode''])
    op.create_index(''idx_sessions_user_started'', ''sessions'', [''user_id'', ''started_at''])
    op.create_index(op.f(''ix_sessions_started_at''), ''sessions'', [''started_at''], unique=False)
    op.create_index(op.f(''ix_sessions_user_id''), ''sessions'', [''user_id''], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f(''ix_sessions_user_id''), table_name=''sessions'')
    op.drop_index(op.f(''ix_sessions_started_at''), table_name=''sessions'')
    op.drop_index(''idx_sessions_user_started'', table_name=''sessions'')
    op.drop_index(''idx_sessions_mode'', table_name=''sessions'')
    op.drop_index(''idx_sessions_category'', table_name=''sessions'')
    
    # Drop table
    op.drop_table(''sessions'')
