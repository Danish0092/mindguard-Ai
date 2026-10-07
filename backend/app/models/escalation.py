import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base
from app.models.enums import CaseStatus, RiskTier


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    output_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_outputs.id"),
        nullable=False,
    )

    tier: Mapped[RiskTier] = mapped_column(
        Enum(RiskTier, name="risk_tier"),
        nullable=False,
    )

    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status"),
        default=CaseStatus.OPEN,
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    counselor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    outcome: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # Relationships
    student = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="escalations",
    )

    counselor = relationship(
        "User",
        foreign_keys=[counselor_id],
        back_populates="assigned_cases",
    )

    output = relationship(
        "AgentOutput",
        back_populates="escalations",
    )