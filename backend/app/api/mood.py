
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi import Query
from sqlalchemy import select
from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.assessment import Assessment
from app.models.user import User
from app.services.mood_trend_service import get_mood_trends
from app.schemas.mood import (
    MoodCheckInRequest,
    MoodCheckInResponse,
)
from app.services.mood_analysis_service import analyze_mood

router = APIRouter(prefix="/mood", tags=["Mood Analysis"])
logger = logging.getLogger(__name__)


@router.post(
    "/check-in",
    response_model=MoodCheckInResponse,
)
def create_mood_check_in(
    data: MoodCheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = analyze_mood(data.message)
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="Mood analysis returned an invalid result.",
        ) from exc
    except Exception as exc:
        logger.exception("Mood analysis failed")
        raise HTTPException(
            status_code=502,
            detail="Mood analysis is temporarily unavailable.",
        ) from exc

    assessment = Assessment(
        student_id=current_user.id,
        assessment_type="mood_check_in",
        score=result["intensity"],
        severity=None,
        responses={
            "mood": result["mood"],
            "contributing_factors": result["contributing_factors"],
            "student_reported": result["student_reported"],
            "summary": result["summary"],
            "model": result["model"],
            "prompt_version": result["prompt_version"],
        },
        completed_at=datetime.now(timezone.utc),
    )

    try:
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to save mood assessment")
        raise HTTPException(
            status_code=500,
            detail="Could not save mood check-in.",
        ) from exc

    return MoodCheckInResponse(
        id=str(assessment.id),
        assessment_type=assessment.assessment_type,
        mood=result["mood"],
        intensity=result["intensity"],
        contributing_factors=result["contributing_factors"],
        student_reported=result["student_reported"],
        summary=result["summary"],
        created_at=assessment.created_at.isoformat(),
    )


@router.get("/history")
def get_mood_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessments = db.scalars(
        select(Assessment)
        .where(
            Assessment.student_id == current_user.id,
            Assessment.assessment_type == "mood_check_in",
        )
        .order_by(
            Assessment.created_at.desc(),
            Assessment.id.desc(),
        )
        .offset(offset)
        .limit(limit)
    ).all()

    history = []

    for assessment in assessments:
        responses = assessment.responses or {}

        history.append({
            "id": str(assessment.id),
            "mood": responses.get("mood", "unclear"),
            "intensity": assessment.score,
            "contributing_factors": responses.get(
                "contributing_factors", []
            ),
            "student_reported": responses.get(
                "student_reported", False
            ),
            "summary": responses.get("summary", ""),
            "created_at": (
                assessment.created_at.isoformat()
                if assessment.created_at
                else None
            ),
        })

    return {
        "items": history,
        "limit": limit,
        "offset": offset,
        "count": len(history),
    }

@router.get("/trends")
def read_mood_trends(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_mood_trends(
        db=db,
        student_id=current_user.id,
        days=days,
    )
