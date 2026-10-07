from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class InterventionLog(Base):
    __tablename__ = "intervention_logs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    intervention_id: Mapped[UUID] = mapped_column(
        ForeignKey("interventions.id", ondelete="CASCADE"),
        nullable=False,
    )

    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    completed: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    effectiveness_rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    outcome: Mapped[dict | None] = mapped_column(
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

    intervention = relationship(
        "Intervention",
        back_populates="logs",
    )

    student = relationship(
        "User",
        back_populates="intervention_logs",
    )