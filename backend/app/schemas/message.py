from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import MessageRole


class MessageCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=10000,
    )


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    student_id: UUID
    seq: int
    role: MessageRole
    content: str
    token_count: int | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }