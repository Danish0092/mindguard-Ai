
from pydantic import BaseModel, Field


class MoodCheckInRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


class MoodCheckInResponse(BaseModel):
    id: str
    assessment_type: str
    mood: str
    intensity: int
    contributing_factors: list[str]
    student_reported: bool
    summary: str
    created_at: str
