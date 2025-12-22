"""Add sessions table for voice/video tracking

Revision ID: f0a1b2c3d4e5
Revises: 5b55184017c9
Create Date: 2025-12-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f0a1b2c3d4e5'
down_revision: Union[str, None] = '5b55184017c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('counselor_category', sa.String(100), nullable=False),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('room_name', sa.String(100), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('room_name')
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_sessions_user_id', 'sessions')
    op.drop_table('sessions')
