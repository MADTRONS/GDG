#!/usr/bin/env python3
"""Seed script to create initial super admin user.

This script creates a default super admin account using environment-configured
credentials. Run this once after deploying the application.

Usage:
    python scripts/seed_admin.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    DEFAULT_ADMIN_EMAIL: Admin email (default: admin@example.com)
    DEFAULT_ADMIN_PASSWORD: Admin password (default: changeme123)
"""
import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.admin import Admin, AdminRole


# Configuration from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/avatar')
DEFAULT_ADMIN_EMAIL = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'changeme123')


async def seed_default_admin() -> None:
    """Create default super admin if not exists."""
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(Admin).where(Admin.email == DEFAULT_ADMIN_EMAIL.lower())
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print(f'✓ Admin user "{DEFAULT_ADMIN_EMAIL}" already exists. Skipping.')
            return

        # Hash password
        password_hash = bcrypt.hashpw(
            DEFAULT_ADMIN_PASSWORD.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Create default admin
        admin = Admin(
            email=DEFAULT_ADMIN_EMAIL.lower(),
            password_hash=password_hash,
            role=AdminRole.SUPER_ADMIN,
            is_active=True
        )

        session.add(admin)
        await session.commit()

        print('=' * 60)
        print('✓ Created default super admin:')
        print(f'  Email: {DEFAULT_ADMIN_EMAIL}')
        print(f'  Password: {DEFAULT_ADMIN_PASSWORD}')
        print('=' * 60)
        print('⚠️  IMPORTANT: Change this password immediately after first login!')
        print('=' * 60)

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(seed_default_admin())
