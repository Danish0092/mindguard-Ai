from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole
from uuid import UUID

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=100)
    university: str | None = Field(default=None, max_length=150)
    role: UserRole = UserRole.STUDENT


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str
    role: UserRole
    university: str | None = None

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
        },
    }