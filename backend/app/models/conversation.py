import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base
from app.models.enums import RiskTier


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    is_checkin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    message_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    min_wellness: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    peak_risk: Mapped[RiskTier] = mapped_column(
        Enum(RiskTier, name="risk_tier"),
        default=RiskTier.NONE,
        nullable=False,
    )

    student = relationship(
        "User",
        back_populates="conversations",
    )
    messages = relationship(
    "Message",
    back_populates="conversation",
    cascade="all, delete-orphan",
)
    agent_outputs = relationship(
    "AgentOutput",
    back_populates="conversation",
)