"""Create a test student user for system testing."""
import asyncio
import sys
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User

# Fix Windows event loop issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def create_test_user():
    async for db in get_db():
        from sqlalchemy import select
        
        # Username format: \domain\username (with escaped backslashes in DB)
        username = r'\university\student'
        
        # Check if test user already exists
        result = await db.execute(select(User).where(User.username == username))
        existing = result.scalar_one_or_none()
        
        if existing:
            print('✅ Test user already exists!')
            print(f'Username: {existing.username}')
            print(f'Blocked: {existing.is_blocked}')
            print('\n🔑 Login Credentials:')
            print(r'Username: \university\student')
            print('Password: Test123!')
        else:
            # Create test user
            password_hash = bcrypt.hashpw('Test123!'.encode(), bcrypt.gensalt()).decode()
            user = User(
                username=username,
                password_hash=password_hash,
                is_blocked=False
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            print('✅ Test user created successfully!')
            print(f'ID: {user.id}')
            print(f'Username: {user.username}')
            print('\n🔑 Login Credentials:')
            print(r'Username: \university\student')
            print('Password: Test123!')
        break

if __name__ == '__main__':
    asyncio.run(create_test_user())
