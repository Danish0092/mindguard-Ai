from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base

from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    university: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Student fields
    program: Mapped[str | None] = mapped_column(String, nullable=True)

    year_of_study: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    preferred_language: Mapped[str | None] = mapped_column(
        String,
        default="en",
        nullable=True,
    )

    emergency_contact: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    checkin_hour: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Counselor fields
    is_on_call: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    last_seen_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    conversations = relationship(
    "Conversation",
    back_populates="student",
)
    messages = relationship(
    "Message",
    back_populates="student",
)
    agent_outputs = relationship(
    "AgentOutput",
    back_populates="student",
)
    escalations = relationship(
    "Escalation",
    foreign_keys="Escalation.student_id",
    back_populates="student",
)

    assigned_cases = relationship(
    "Escalation",
    foreign_keys="Escalation.counselor_id",
    back_populates="counselor",
)
    assigned_cases = relationship(
    "Escalation",
    foreign_keys="Escalation.counselor_id",
    back_populates="counselor",
)
    student_memory = relationship(
    "StudentMemory",
    back_populates="student",
    uselist=False,
    cascade="all, delete-orphan",
)
    consent = relationship(
    "Consent",
    back_populates="student",
    uselist=False,
    cascade="all, delete-orphan",
)
    assessments = relationship(
    "Assessment",
    back_populates="student",
    cascade="all, delete-orphan",
)
    interventions = relationship(
    "Intervention",
    back_populates="student",
    cascade="all, delete-orphan",
)
    intervention_logs = relationship(
    "InterventionLog",
    back_populates="student",
    cascade="all, delete-orphan",
)
    notifications = relationship(
    "Notification",
    back_populates="user",
    cascade="all, delete-orphan",
)
    audit_logs = relationship(
    "AuditLog",
    back_populates="user",
)
