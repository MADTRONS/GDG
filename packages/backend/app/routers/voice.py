"""Voice calling router for creating Daily.co rooms and spawning PipeCat bots."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, UUID4
from typing import Dict
import uuid

from app.database import get_db
from app.utils.dependencies import get_current_user
from app.services.daily_service import DailyService
from app.services.pipecat_service import PipeCatService
from app.repositories.session_repository import SessionRepository
from app.repositories.counselor_repository import CounselorRepository

router = APIRouter(prefix="/voice", tags=["voice"])


class CreateRoomRequest(BaseModel):
    """Request schema for creating a voice room."""
    counselor_category: UUID4


class CreateRoomResponse(BaseModel):
    """Response schema for room creation."""
    room_url: str
    user_token: str
    room_name: str
    session_id: UUID4


@router.post(
    "/create-room",
    response_model=CreateRoomResponse,
    summary="Create voice calling room",
    description="Creates a Daily.co room and spawns PipeCat bot for voice counseling session.",
    status_code=status.HTTP_201_CREATED
)
async def create_room(
    request: CreateRoomRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a voice calling session room.
    
    Flow:
    1. Validates counselor category exists and is enabled
    2. Creates Daily.co room with temporary access (24h expiration)
    3. Generates user token for student and bot token for PipeCat
    4. Spawns PipeCat bot instance with configured LLM/TTS/STT
    5. Logs session to database
    6. Returns room credentials to frontend
    
    Args:
        request: Request containing counselor category ID
        current_user: Authenticated user from JWT
        db: Database session
        
    Returns:
        Room credentials including URL, token, and session ID
        
    Raises:
        HTTPException 404: If counselor category not found or disabled
        HTTPException 500: If room creation or bot spawn fails
    """
    # Initialize services
    daily_service = DailyService()
    counselor_repo = CounselorRepository(db)
    pipecat_service = PipeCatService(counselor_repo)
    session_repo = SessionRepository(db)
    
    # Generate unique identifiers
    session_id = uuid.uuid4()
    room_name = f"voice-{session_id}"
    
    try:
        # Verify category exists and is enabled
        category = await counselor_repo.get_by_id(str(request.counselor_category))
        if not category or not category.enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Counselor category not found or disabled"
            )
        
        # Create Daily.co room
        room_data = await daily_service.create_room(room_name)
        room_url = room_data["room_url"]
        
        # Generate tokens
        user_token = await daily_service.create_user_token(
            room_name,
            current_user["user_id"]
        )
        bot_token = await daily_service.create_bot_token(room_name)
        
        # Spawn PipeCat bot
        bot_info = await pipecat_service.spawn_bot(
            room_url=room_url,
            bot_token=bot_token,
            session_id=str(session_id),
            category_id=str(request.counselor_category)
        )
        
        # Log session to database
        await session_repo.create_session(
            session_id=session_id,
            user_id=uuid.UUID(current_user["user_id"]),
            counselor_category=category.name,
            mode="voice",
            room_name=room_name
        )
        
        return CreateRoomResponse(
            room_url=room_url,
            user_token=user_token,
            room_name=room_name,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Invalid category ID from PipeCat service
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Log error with full context for debugging
        import traceback
        error_detail = f"Failed to create voice session: {str(e)}"
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
