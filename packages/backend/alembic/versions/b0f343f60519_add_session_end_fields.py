"""add_session_end_fields

Revision ID: b0f343f60519
Revises: 5b55184017c9
Create Date: 2025-12-22 13:46:24.371108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b0f343f60519'
down_revision: Union[str, None] = '5b55184017c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add crisis_detected column with default False
    op.add_column('sessions', sa.Column('crisis_detected', sa.Boolean(), nullable=False, server_default=sa.false()))
    
    # Change transcript from Text to JSONB
    # First create a new column
    op.add_column('sessions', sa.Column('transcript_jsonb', postgresql.JSONB(), nullable=True))
    
    # Drop the old text column (safe since this is a new feature)
    op.drop_column('sessions', 'transcript')
    
    # Rename the new column to transcript
    op.alter_column('sessions', 'transcript_jsonb', new_column_name='transcript')


def downgrade() -> None:
    # Revert transcript back to Text
    op.add_column('sessions', sa.Column('transcript_text', sa.Text(), nullable=True))
    op.drop_column('sessions', 'transcript')
    op.alter_column('sessions', 'transcript_text', new_column_name='transcript')
    
    # Drop crisis_detected column
    op.drop_column('sessions', 'crisis_detected')
