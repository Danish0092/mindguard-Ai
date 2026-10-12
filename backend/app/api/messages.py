import time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent_output import AgentOutput
from app.models.conversation import Conversation
from app.models.enums import (
    AgentKind,
    CaseStatus,
    MessageRole,
    RiskTier,
    UserRole,
)
from app.models.escalation import Escalation
from app.models.message import Message
from app.models.notification import Notification
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.agent_graph import mindguard_graph
from app.services.memory_service import get_student_memory
from app.services.memory_update_service import update_student_memory

router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"],
)


@router.post(
    "",
    response_model=list[MessageResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    conversation_id: UUID,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Verify conversation ownership
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.student_id == current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # 2. Save the student's message
    student_seq = conversation.message_count + 1

    student_message = Message(
        conversation_id=conversation.id,
        student_id=current_user.id,
        seq=student_seq,
        role=MessageRole.STUDENT,
        content=data.content,
    )

    conversation.message_count = student_seq
    db.add(student_message)
    db.commit()
    db.refresh(student_message)

    # 3. Retrieve the student's saved memory
    try:
        student_memory = get_student_memory(
            db=db,
            student_id=current_user.id,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve student memory.",
        ) from exc

    # 4. Run the LangGraph workflow
    start_time = time.perf_counter()

    try:
        graph_result = mindguard_graph.invoke(
            {
                "student_id": str(current_user.id),
                "conversation_id": str(conversation.id),
                "message": data.content,
                "memory": student_memory,
                "screening": {},
                "flagged": False,
                "response": "",
                "route": "",
                "response_metadata": {},
            }
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The AI workflow is temporarily unavailable. "
                "If you need immediate help, contact a trusted person "
                "or local emergency services."
            ),
        ) from exc

    workflow_latency = int(
        (time.perf_counter() - start_time) * 1000
    )

    screening = graph_result["screening"]
    flagged = graph_result["flagged"]
    assistant_text = graph_result["response"]

    # 5. Save the crisis-screening result
    crisis_output = AgentOutput(
        message_id=student_message.id,
        conversation_id=conversation.id,
        student_id=current_user.id,
        agent=AgentKind.CRISIS_DETECTION,
        risk_tier=(
            RiskTier.HIGH if flagged else RiskTier.NONE
        ),
        result=screening,
        prompt_version="crisis-rules-v1",
        model="rule-based",
        latency_ms=workflow_latency,
        total_tokens=None,
    )

    db.add(crisis_output)
    db.flush()

    # 6. Handle a flagged message
    if flagged:
        db.scalar(
            select(User)
            .where(User.id == current_user.id)
            .with_for_update()
        )

        active_case = db.scalar(
            select(Escalation)
            .where(
                Escalation.student_id == current_user.id,
                Escalation.status.in_(
                    [
                        CaseStatus.OPEN,
                        CaseStatus.ACKNOWLEDGED,
                    ]
                ),
            )
            .with_for_update()
        )

        if active_case is None:
            counselor = db.scalar(
                select(User)
                .where(
                    User.role == UserRole.COUNSELOR,
                    User.university == current_user.university,
                    User.is_active.is_(True),
                    User.is_on_call.is_(True),
                )
                .order_by(User.created_at.asc())
                .limit(1)
            )

            active_case = Escalation(
                student_id=current_user.id,
                output_id=crisis_output.id,
                tier=RiskTier.HIGH,
                status=CaseStatus.OPEN,
                summary=(
                    "Automated prototype screening flagged a "
                    "message for urgent human review."
                ),
                counselor_id=(
                    counselor.id if counselor else None
                ),
            )

            db.add(active_case)
            db.flush()

            if counselor:
                db.add(
                    Notification(
                        user_id=counselor.id,
                        notification_type="crisis_alert",
                        title="Crisis case requires review",
                        message=(
                            "A student message was flagged "
                            "for urgent human review."
                        ),
                        data={
                            "escalation_id": str(active_case.id),
                            "student_id": str(current_user.id),
                        },
                    )
                )

        # Keep the crisis response from LangGraph
        assistant_seq = conversation.message_count + 1

        assistant_message = Message(
            conversation_id=conversation.id,
            student_id=current_user.id,
            seq=assistant_seq,
            role=MessageRole.ASSISTANT,
            content=assistant_text,
        )

        conversation.message_count = assistant_seq
        conversation.peak_risk = RiskTier.HIGH

        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        return [student_message, assistant_message]

    # 7. Save the normal AI response and metadata
    ai_result = graph_result["response_metadata"]

    assistant_seq = conversation.message_count + 1

    assistant_message = Message(
        conversation_id=conversation.id,
        student_id=current_user.id,
        seq=assistant_seq,
        role=MessageRole.ASSISTANT,
        content=assistant_text,
    )

    conversation.message_count = assistant_seq

    conversation_output = AgentOutput(
        message_id=assistant_message.id,
        conversation_id=conversation.id,
        student_id=current_user.id,
        agent=AgentKind.CONVERSATION,
        risk_tier=RiskTier.NONE,
        result={"response": assistant_text},
        prompt_version=ai_result.get(
            "prompt_version", "unknown"
        ),
        model=ai_result.get("model", "unknown"),
        latency_ms=ai_result.get(
            "latency_ms", workflow_latency
        ),
        total_tokens=ai_result.get("total_tokens"),
    )


    db.add(assistant_message)
    db.add(conversation_output)
    db.commit()
    db.refresh(assistant_message)

    # 8. Update memory after saving the chat response.
    # Memory failure must not break the conversation.
    try:
        update_student_memory(
            db=db,
            student_id=current_user.id,
            message=data.content,
        )
    except Exception:
        db.rollback()
        # TODO: Add application logging for memory-update failures.

    return [student_message, assistant_message]



@router.get("", response_model=list[MessageResponse])
def get_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify conversation ownership
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.student_id == current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.student_id == current_user.id,
        )
        .order_by(Message.seq.asc())
    ).all()

    return list(messages)
