"""Check if user exists in database."""
import asyncio
import sys
from app.database import get_db
from app.models.user import User
from sqlalchemy import select

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def check_users():
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        if users:
            print(f"\n✅ Found {len(users)} user(s) in database:")
            for user in users:
                print(f"   - Username: {user.username}")
                print(f"     Blocked: {user.is_blocked}")
                print(f"     Created: {user.created_at}")
        else:
            print("\n❌ No users found in database!")
        break

if __name__ == '__main__':
    asyncio.run(check_users())
