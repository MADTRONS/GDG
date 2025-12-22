"""add_quality_metrics_to_sessions

Revision ID: 672c05922909
Revises: 200f48cc05b4
Create Date: 2025-12-22 20:24:35.766211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '672c05922909'
down_revision: Union[str, None] = '200f48cc05b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add quality_metrics column as JSONB
    op.add_column('sessions', sa.Column('quality_metrics', postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    # Remove quality_metrics column
    op.drop_column('sessions', 'quality_metrics')
