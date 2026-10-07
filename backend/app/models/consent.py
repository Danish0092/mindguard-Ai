from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    data_consent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    ai_consent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    counselor_consent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    emergency_contact_consent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    consented_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
        back_populates="consent",
    )