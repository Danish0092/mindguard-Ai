
from collections import Counter
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment import Assessment


def get_mood_trends(
    db: Session,
    student_id: UUID,
    days: int = 7,
) -> dict:
    """Summarize a student's self-reported mood check-ins."""

    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    assessments = db.scalars(
        select(Assessment)
        .where(
            Assessment.student_id == student_id,
            Assessment.assessment_type == "mood_check_in",
            Assessment.created_at >= start_date,
            Assessment.created_at <= now,
        )
        .order_by(Assessment.created_at.asc())
    ).all()

    mood_counts = Counter()
    intensity_values = []
    timeline = []

    for assessment in assessments:
        responses = assessment.responses or {}
        mood = responses.get("mood", "unclear")

        if not isinstance(mood, str):
            mood = "unclear"

        mood = mood.strip().lower() or "unclear"

        mood_counts[mood] += 1

        # Exclude unclear or invalid intensity values from averages.
        score = assessment.score

        if (
            isinstance(score, int)
            and not isinstance(score, bool)
            and 1 <= score <= 5
            and mood != "unclear"
        ):
            intensity_values.append({
                "score": score,
                "created_at": assessment.created_at,
            })

        timeline.append({
            "mood": mood,
            "intensity": (
                score
                if isinstance(score, int)
                and not isinstance(score, bool)
                and 1 <= score <= 5
                else None
            ),
            "created_at": (
                assessment.created_at.isoformat()
                if assessment.created_at
                else None
            ),
        })

    average_intensity = (
        round(
            sum(item["score"] for item in intensity_values)
            / len(intensity_values),
            2,
        )
        if intensity_values
        else None
    )

    # Compare the older and newer halves of the available check-ins.
    midpoint = len(intensity_values) // 2
    trend = "insufficient_data"
    earlier_average = None
    recent_average = None

    if len(intensity_values) >= 4:
        earlier = intensity_values[:midpoint]
        recent = intensity_values[midpoint:]

        earlier_average = round(
            sum(item["score"] for item in earlier) / len(earlier),
            2,
        )
        recent_average = round(
            sum(item["score"] for item in recent) / len(recent),
            2,
        )

        difference = recent_average - earlier_average

        if difference >= 0.5:
            trend = "higher_intensity"
        elif difference <= -0.5:
            trend = "lower_intensity"
        else:
            trend = "similar_intensity"

    return {
        "period_days": days,
        "check_in_count": len(assessments),
        "scored_check_in_count": len(intensity_values),
        "average_intensity": average_intensity,
        "mood_distribution": dict(mood_counts),
        "intensity_trend": {
            "label": trend,
            "earlier_average": earlier_average,
            "recent_average": recent_average,
        },
        "timeline": timeline,
        "note": (
            "These summaries describe recorded check-ins only. "
            "They are not a clinical assessment or a validated "
            "measure of overall wellness."
        ),
    }
