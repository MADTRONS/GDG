"""User schemas for API responses."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    \"\"\"User data for API responses (excludes sensitive fields).\"\"\"
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    is_blocked: bool
    created_at: datetime
    updated_at: datetime
