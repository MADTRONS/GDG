import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.admin import Admin, AdminRole

async def create_admin():
    async for db in get_db():
        from sqlalchemy import select
        result = await db.execute(select(Admin).where(Admin.email == 'admin@example.com'))
        existing = result.scalar_one_or_none()
        
        if existing:
            print('Admin already exists: admin@example.com')
        else:
            password_hash = bcrypt.hashpw('Admin123!'.encode(), bcrypt.gensalt()).decode()
            admin = Admin(email='admin@example.com', password_hash=password_hash, role=AdminRole.SUPER_ADMIN, is_active=True)
            db.add(admin)
            await db.commit()
            print('Admin created!')
            print('Email: admin@example.com')
            print('Password: Admin123!')
        break

if __name__ == '__main__':
    asyncio.run(create_admin())

