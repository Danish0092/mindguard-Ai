from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student_memory import StudentMemory


def get_student_memory(
    db: Session,
    student_id: UUID,
) -> dict:
    """
    Retrieve the saved memory for a student.
    Returns an empty dictionary if no memory exists.
    """
    memory = db.scalar(
        select(StudentMemory).where(
            StudentMemory.student_id == student_id
        )
    )

    if memory is None:
        return {}

    return {
        "wellness_trend": (
            memory.wellness_trend.value
            if memory.wellness_trend
            else None
        ),
        "baseline_wellness": memory.baseline_wellness,
        "current_wellness": memory.current_wellness,
        "triggers": memory.triggers or [],
        "effective_interventions": (
            memory.effective_interventions or []
        ),
        "ineffective_interventions": (
            memory.ineffective_interventions or []
        ),
        "phq9_severity": memory.phq9_severity,
        "context_card": memory.context_card or {},
        "pattern_findings": memory.pattern_findings or {},
    }