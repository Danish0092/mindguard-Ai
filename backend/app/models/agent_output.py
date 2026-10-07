import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base
from app.models.enums import AgentKind, RiskTier, SeverityBand


class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=True,
    )

    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=True,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    agent: Mapped[AgentKind] = mapped_column(
        Enum(AgentKind, name="agent_kind"),
        nullable=False,
    )

    # AI analysis fields
    wellness_score: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    sentiment: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 3),
        nullable=True,
    )

    primary_emotion: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    depression_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    severity: Mapped[SeverityBand | None] = mapped_column(
    Enum(
        SeverityBand,
        name="severity_band",
        values_callable=lambda enum_class: [
            item.value for item in enum_class
        ],
        create_type=False,
    ),
    nullable=True,
)

    risk_tier: Mapped[RiskTier | None] = mapped_column(
    Enum(
        RiskTier,
        name="risk_tier",
        values_callable=lambda enum_class: [
            item.value for item in enum_class
        ],
        create_type=False,
    ),
    nullable=True,
)

    # Complete agent response
    result: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    prompt_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # Performance information
    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    student = relationship(
        "User",
        back_populates="agent_outputs",
    )

    message = relationship(
        "Message",
        back_populates="agent_outputs",
    )

    conversation = relationship(
        "Conversation",
        back_populates="agent_outputs",
    )

    escalations = relationship(
    "Escalation",
    back_populates="output",
)

    __table_args__ = (
        UniqueConstraint(
            "message_id",
            "agent",
            name="uq_agent_outputs_message_agent",
        ),
    )