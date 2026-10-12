
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.enums import CaseStatus, UserRole
from app.models.escalation import Escalation
from app.models.user import User


router = APIRouter(
    prefix="/escalations",
    tags=["Escalations"],
)


class ResolveCaseRequest(BaseModel):
    outcome: str = Field(min_length=3, max_length=2000)


def require_counselor(current_user: User) -> None:
    if (
        current_user.role != UserRole.COUNSELOR
        or not current_user.is_active
    ):
        raise HTTPException(
            status_code=403,
            detail="Only active counselors can manage cases",
        )


def get_case_for_update(
    escalation_id: UUID,
    db: Session,
) -> Escalation:
    case = db.scalar(
        select(Escalation)
        .where(Escalation.id == escalation_id)
        .with_for_update()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        )

    return case


def case_response(case: Escalation) -> dict:
    return {
        "id": str(case.id),
        "student_id": str(case.student_id),
        "counselor_id": (
            str(case.counselor_id)
            if case.counselor_id
            else None
        ),
        "tier": case.tier.value,
        "status": case.status.value,
        "summary": case.summary,
        "outcome": case.outcome,
        "opened_at": case.opened_at,
        "acknowledged_at": case.acknowledged_at,
        "resolved_at": case.resolved_at,
    }


@router.patch("/{escalation_id}/acknowledge")
def acknowledge_case(
    escalation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_counselor(current_user)

    try:
        case = get_case_for_update(escalation_id, db)

        if case.status == CaseStatus.RESOLVED:
            raise HTTPException(
                status_code=409,
                detail="Resolved cases cannot be acknowledged",
            )

        if case.status == CaseStatus.FALSE_POSITIVE:
            raise HTTPException(
                status_code=409,
                detail="False-positive cases cannot be acknowledged",
            )

        if case.counselor_id not in (None, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="This case is assigned to another counselor",
            )

        # Claim the case if it is currently unassigned.
        if case.counselor_id is None:
            case.counselor_id = current_user.id

        if case.status == CaseStatus.OPEN:
            case.status = CaseStatus.ACKNOWLEDGED
            case.acknowledged_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(case)

        return case_response(case)

    except Exception:
        db.rollback()
        raise


@router.patch("/{escalation_id}/resolve")
def resolve_case(
    escalation_id: UUID,
    data: ResolveCaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_counselor(current_user)

    try:
        case = get_case_for_update(escalation_id, db)

        if case.status == CaseStatus.RESOLVED:
            raise HTTPException(
                status_code=409,
                detail="This case is already resolved",
            )

        if case.status == CaseStatus.FALSE_POSITIVE:
            raise HTTPException(
                status_code=409,
                detail="False-positive cases cannot be resolved",
            )

        if case.counselor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the assigned counselor can resolve this case",
            )

        if case.status != CaseStatus.ACKNOWLEDGED:
            raise HTTPException(
                status_code=409,
                detail="A case must be acknowledged before resolution",
            )

        case.status = CaseStatus.RESOLVED
        case.outcome = data.outcome.strip()
        case.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(case)

        return case_response(case)

    except Exception:
        db.rollback()
        raise
