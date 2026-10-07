from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    assessment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    responses: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    student = relationship(
        "User",
        back_populates="assessments",
    )