from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    is_checkin: bool = False


class ConversationResponse(BaseModel):
    id: UUID
    student_id: UUID
    is_checkin: bool
    started_at: datetime
    ended_at: datetime | None
    message_count: int
    summary: str | None
    min_wellness: int | None
    peak_risk: str

    model_config = {
        "from_attributes": True,
    }