"""User repository for database operations."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            User object if found, None otherwise

        Example:
            >>> repo = UserRepository(session)
            >>> user = await repo.get_by_username(r'\\COLLEGE\\jdoe')
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()