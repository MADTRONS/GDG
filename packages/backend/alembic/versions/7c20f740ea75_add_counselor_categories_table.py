"""add_counselor_categories_table

Revision ID: 7c20f740ea75
Revises: df870ce3dc0f
Create Date: 2025-12-21 00:38:55.791994

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7c20f740ea75'
down_revision: Union[str, None] = 'df870ce3dc0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create counselor_categories table
    counselor_categories_table = op.create_table(
        'counselor_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon_name', sa.String(length=50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create indexes
    op.create_index('idx_counselor_categories_name', 'counselor_categories', ['name'], unique=False)
    op.create_index('idx_counselor_categories_enabled', 'counselor_categories', ['enabled'], unique=False)
    
    # Seed initial categories
    op.bulk_insert(
        counselor_categories_table,
        [
            {
                'id': uuid.uuid4(),
                'name': 'Health',
                'description': 'Mental health, stress management, wellness, and self-care support. Get help with anxiety, depression, sleep issues, and maintaining overall well-being.',
                'icon_name': 'heart-pulse',
                'enabled': True,
            },
            {
                'id': uuid.uuid4(),
                'name': 'Career',
                'description': 'Career exploration, job search strategies, resume help, and interview preparation. Plan your professional future with expert guidance.',
                'icon_name': 'briefcase',
                'enabled': True,
            },
            {
                'id': uuid.uuid4(),
                'name': 'Academic',
                'description': 'Study strategies, time management, course selection, and academic planning. Improve your learning effectiveness and achieve academic success.',
                'icon_name': 'graduation-cap',
                'enabled': True,
            },
            {
                'id': uuid.uuid4(),
                'name': 'Financial',
                'description': 'Budgeting, student loans, financial aid, and money management. Build healthy financial habits and navigate college expenses confidently.',
                'icon_name': 'dollar-sign',
                'enabled': True,
            },
            {
                'id': uuid.uuid4(),
                'name': 'Social',
                'description': 'Relationships, communication skills, campus involvement, and social well-being. Navigate friendships, roommate conflicts, and build meaningful connections.',
                'icon_name': 'users',
                'enabled': True,
            },
            {
                'id': uuid.uuid4(),
                'name': 'Personal Development',
                'description': 'Goal setting, self-awareness, life skills, and personal growth. Discover your strengths, values, and create a roadmap for your future.',
                'icon_name': 'star',
                'enabled': True,
            },
        ]
    )


def downgrade() -> None:
    op.drop_index('idx_counselor_categories_enabled', table_name='counselor_categories')
    op.drop_index('idx_counselor_categories_name', table_name='counselor_categories')
    op.drop_table('counselor_categories')
