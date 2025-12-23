"""Video session router for LiveKit room creation."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
import uuid

from app.database import get_db
from app.utils.dependencies import get_current_user
from app.services.livekit_service import LiveKitService
from app.services.avatar_service import AvatarService
from app.repositories.session_repository import SessionRepository
from app.repositories.counselor_repository import CounselorRepository
from app.config import get_settings


router = APIRouter(prefix="/video", tags=["video"])


class CreateRoomRequest(BaseModel):
    """Request model for creating a video room."""
    counselor_category: UUID4


class CreateRoomResponse(BaseModel):
    """Response model for video room creation."""
    room_url: str
    access_token: str
    room_name: str
    session_id: UUID4
    avatar_id: str


@router.post(
    "/create-room",
    response_model=CreateRoomResponse,
    summary="Create video calling room",
    description="Creates a LiveKit room and spawns Beyond Presence avatar for video counseling session."
)
async def create_room(
    request: CreateRoomRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a video calling session room.
    
    1. Validates counselor category exists
    2. Creates LiveKit room
    3. Generates access token for student
    4. Spawns Beyond Presence avatar agent
    5. Logs session to database
    6. Returns room credentials to frontend
    
    Args:
        request: CreateRoomRequest with counselor_category
        current_user: Authenticated user from JWT
        db: Database session
        
    Returns:
        CreateRoomResponse with room credentials
        
    Raises:
        HTTPException 404: If counselor category not found or disabled
        HTTPException 500: If room creation or avatar spawn fails
    """
    # Initialize services and repositories
    livekit_service = LiveKitService()
    counselor_repo = CounselorRepository(db)
    avatar_service = AvatarService(counselor_repo)
    session_repo = SessionRepository(db)
    settings = get_settings()
    
    # Generate unique identifiers
    session_id = uuid.uuid4()
    room_name = f"video-{session_id}"
    
    try:
        # Verify category exists and is enabled
        category = await counselor_repo.get_by_id(request.counselor_category)
        if not category or not category.enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Counselor category not found or disabled"
            )
        
        # Create LiveKit room
        room_data = await livekit_service.create_room(room_name)
        
        # Generate access token for student
        access_token = await livekit_service.generate_access_token(
            room_name=room_name,
            participant_identity=current_user["user_id"],
            participant_name=f"Student_{current_user['username']}"
        )
        
        # Spawn Beyond Presence avatar agent
        avatar_info = await avatar_service.spawn_avatar(
            room_name=room_name,
            session_id=str(session_id),
            category_id=str(request.counselor_category)
        )
        
        # Log session to database
        await session_repo.create_session(
            session_id=session_id,
            user_id=uuid.UUID(current_user["user_id"]),
            counselor_category=category.name,
            mode="video",
            room_name=room_name
        )
        
        # Construct room URL
        room_url = settings.livekit_url.replace("wss://", "https://").replace("ws://", "http://")
        
        # Get avatar_id from settings or use default
        avatar_id = settings.avatar_id or settings.bey_avatar_id or '55590705-9528-4022-9550-70b724c962d8'
        
        return CreateRoomResponse(
            room_url=room_url,
            access_token=access_token,
            room_name=room_name,
            session_id=session_id,
            avatar_id=avatar_id
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Category validation errors
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Log error with full context
        print(f"Error creating video room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create video session: {str(e)}"
        )
