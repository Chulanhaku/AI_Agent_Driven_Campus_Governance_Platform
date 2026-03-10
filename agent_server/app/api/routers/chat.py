from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.api.schemas.chat import (
    ChatConfirmRequestSchema,
    ChatHistoryResponseSchema,
    ChatSendRequestSchema,
    ChatSendResponseSchema,
)
from app.db.models import User
from app.db.repositories.agent_session_repository import AgentSessionRepository
from app.db.repositories.campus_card_repository import CampusCardRepository
from app.db.repositories.pending_action_repository import PendingActionRepository
from app.db.repositories.schedule_repository import ScheduleRepository
from app.services.agent_session_service import AgentSessionService
from app.services.campus_card_service import CampusCardService
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/chat", tags=["chat"])


def get_agent_session_service(db: Session = Depends(get_db_dep)) -> AgentSessionService:
    agent_session_repository = AgentSessionRepository(db)
    pending_action_repository = PendingActionRepository(db)
    schedule_repository = ScheduleRepository(db)
    campus_card_repository = CampusCardRepository(db)

    schedule_service = ScheduleService(schedule_repository)
    campus_card_service = CampusCardService(campus_card_repository)

    return AgentSessionService(
        agent_session_repository=agent_session_repository,
        pending_action_repository=pending_action_repository,
        schedule_service=schedule_service,
        campus_card_service=campus_card_service,
    )


@router.post("/send", response_model=ChatSendResponseSchema)
def send_chat_message(
    request: ChatSendRequestSchema,
    current_user: User = Depends(get_current_user),
    agent_session_service: AgentSessionService = Depends(get_agent_session_service),
) -> ChatSendResponseSchema:
    if not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty",
        )

    try:
        session, user_message, assistant_message, requires_confirmation, action_id = (
            agent_session_service.send_message(
                current_user=current_user,
                content=request.content.strip(),
                session_id=request.session_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ChatSendResponseSchema(
        session_id=session.id,
        user_message=user_message,
        assistant_message=assistant_message,
        requires_confirmation=requires_confirmation,
        action_id=action_id,
    )


@router.post("/confirm", response_model=ChatSendResponseSchema)
def confirm_chat_action(
    request: ChatConfirmRequestSchema,
    current_user: User = Depends(get_current_user),
    agent_session_service: AgentSessionService = Depends(get_agent_session_service),
) -> ChatSendResponseSchema:
    try:
        session, user_message, assistant_message = agent_session_service.confirm_action(
            current_user=current_user,
            session_id=request.session_id,
            action_id=request.action_id,
            approved=request.approved,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ChatSendResponseSchema(
        session_id=session.id,
        user_message=user_message,
        assistant_message=assistant_message,
        requires_confirmation=False,
        action_id=None,
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponseSchema)
def get_chat_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    agent_session_service: AgentSessionService = Depends(get_agent_session_service),
) -> ChatHistoryResponseSchema:
    messages = agent_session_service.list_session_messages(
        session_id=session_id,
        user_id=current_user.id,
    )

    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return ChatHistoryResponseSchema(
        session_id=session_id,
        items=messages,
        total=len(messages),
    )