from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import WellnessTrend


class StudentMemory(Base):
    __tablename__ = "student_memories"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    wellness_trend: Mapped[WellnessTrend] = mapped_column(
        default=WellnessTrend.UNKNOWN,
        nullable=False,
    )

    baseline_wellness: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    current_wellness: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    triggers: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    effective_interventions: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    ineffective_interventions: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    phq9_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    phq9_severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    context_card: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    pattern_findings: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    student = relationship(
        "User",
        back_populates="student_memory",
    )