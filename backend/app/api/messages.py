from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent_output import AgentOutput
from app.models.conversation import Conversation
from app.models.enums import AgentKind, MessageRole
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.ai_service import generate_response


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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Verify that the conversation belongs to
    #    the authenticated student.
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

    # 2. Create the student's message.
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

    # 3. Send the student's message to the AI.
    try:
        ai_result = generate_response(data.content)
    except Exception as exc:
        # The student's message is already safely stored.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service is temporarily unavailable",
        ) from exc

    # 4. Create the assistant's message.
    assistant_seq = conversation.message_count + 1

    assistant_message = Message(
        conversation_id=conversation.id,
        student_id=current_user.id,
        seq=assistant_seq,
        role=MessageRole.ASSISTANT,
        content=ai_result["text"],
    )

    conversation.message_count = assistant_seq

    db.add(assistant_message)

    # 5. Store the AI processing information.
    agent_output = AgentOutput(
        message_id=assistant_message.id,
        conversation_id=conversation.id,
        student_id=current_user.id,
        agent=AgentKind.CONVERSATION,
        result={
            "response": ai_result["text"],
        },
        prompt_version=ai_result["prompt_version"],
        model=ai_result["model"],
        latency_ms=ai_result["latency_ms"],
        total_tokens=ai_result["total_tokens"],
    )

    db.add(agent_output)

    db.commit()

    db.refresh(assistant_message)

    return [
        student_message,
        assistant_message,
    ]


@router.get(
    "",
    response_model=list[MessageResponse],
)
def get_messages(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
            Message.conversation_id == conversation.id
        )
        .order_by(Message.seq.asc())
    ).all()

    return messages