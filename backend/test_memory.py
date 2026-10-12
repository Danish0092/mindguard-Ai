
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.user import User
from app.models.student_memory import StudentMemory
from app.models.enums import WellnessTrend


# Replace this with your registered student email
STUDENT_EMAIL = "test@example.com"

db = SessionLocal()

try:
    student = db.scalar(
        select(User).where(User.email == STUDENT_EMAIL)
    )

    if student is None:
        raise ValueError("Student account not found.")

    memory = db.scalar(
        select(StudentMemory).where(
            StudentMemory.student_id == student.id
        )
    )

    if memory is None:
        memory = StudentMemory(
            student_id=student.id,
            wellness_trend=WellnessTrend.UNKNOWN,
        )
        db.add(memory)

    memory.context_card = {
        "test_memory": True,
        "study_concern": "Exam-related stress",
        "preferred_support": (
            "Practical, step-by-step study planning"
        ),
    }

    db.commit()

    print("Test memory saved successfully.")
    print("Student ID:", student.id)
    print("Context card:", memory.context_card)

except Exception:
    db.rollback()
    raise

finally:
    db.close()
