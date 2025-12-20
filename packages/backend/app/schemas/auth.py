"""Authentication schemas for login requests and responses."""
import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    \"\"\"Login request payload with username and password.\"\"\"
    username: Annotated[str, Field(
        min_length=1,
        max_length=255,
        description='Username in \\\\domain\\\\username format'
    )]
    password: Annotated[str, Field(
        min_length=1,
        description='User password'
    )]

    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        \"\"\"Validate username matches \\\\domain\\\\username format.\"\"\"
        pattern = r'^\\\[^\\\]+\\\[^\\\]+$'
        if not re.match(pattern, v):
            raise ValueError('Username must be in \\\\domain\\\\username format')
        return v


class LoginResponse(BaseModel):
    \"\"\"Login response with access token and user data.\"\"\"
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse
