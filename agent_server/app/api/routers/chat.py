#PLAN A
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep, get_llm_provider, get_retriever
from app.api.schemas.chat import (
    ChatConfirmRequestSchema,
    ChatHistoryResponseSchema,
    ChatSendRequestSchema,
    ChatSendResponseSchema,
)
from app.config.settings import get_settings
from app.db.models import User
from app.db.repositories.agent_session_repository import AgentSessionRepository
from app.db.repositories.audit_log_repository import AuditLogRepository
from app.db.repositories.campus_card_repository import CampusCardRepository
from app.db.repositories.leave_repository import LeaveRepository
from app.db.repositories.pending_action_repository import PendingActionRepository
from app.db.repositories.schedule_repository import ScheduleRepository
from app.db.repositories.tool_execution_log_repository import ToolExecutionLogRepository
from app.llm.base import BaseLlmProvider
from app.rag.retriever import Retriever
from app.services.agent_session_service import AgentSessionService
from app.services.audit_service import AuditService
from app.services.campus_card_service import CampusCardService
from app.services.leave_service import LeaveService
from app.services.schedule_service import ScheduleService
from app.services.tool_execution_log_service import ToolExecutionLogService

router = APIRouter(prefix="/chat", tags=["chat"])


def get_agent_session_service(
    db: Session = Depends(get_db_dep),
    llm_provider: BaseLlmProvider = Depends(get_llm_provider),
    retriever: Retriever = Depends(get_retriever),
) -> AgentSessionService:
    settings = get_settings()

    agent_session_repository = AgentSessionRepository(db)
    pending_action_repository = PendingActionRepository(db)
    schedule_repository = ScheduleRepository(db)
    campus_card_repository = CampusCardRepository(db)
    leave_repository = LeaveRepository(db)
    audit_log_repository = AuditLogRepository(db)
    tool_execution_log_repository = ToolExecutionLogRepository(db)

    schedule_service = ScheduleService(schedule_repository)
    campus_card_service = CampusCardService(campus_card_repository)
    leave_service = LeaveService(leave_repository)
    audit_service = AuditService(audit_log_repository)
    tool_execution_log_service = ToolExecutionLogService(tool_execution_log_repository)

    return AgentSessionService(
        agent_session_repository=agent_session_repository,
        pending_action_repository=pending_action_repository,
        schedule_service=schedule_service,
        campus_card_service=campus_card_service,
        leave_service=leave_service,
        audit_service=audit_service,
        tool_execution_log_service=tool_execution_log_service,
        llm_provider=llm_provider,
        retriever=retriever,
        rag_top_k=settings.rag_top_k,
    )

def get_tool_execution_log_service(
    db: Session = Depends(get_db_dep),
) -> ToolExecutionLogService:
    repository = ToolExecutionLogRepository(db)
    return ToolExecutionLogService(repository)
#plan B


# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.api.deps import get_current_user, get_db_dep, get_llm_provider
# from app.api.schemas.chat import (
#     ChatConfirmRequestSchema,
#     ChatHistoryResponseSchema,
#     ChatSendRequestSchema,
#     ChatSendResponseSchema,
# )
# from app.config.settings import get_settings
# from app.db.models import User
# from app.db.repositories.agent_session_repository import AgentSessionRepository
# from app.db.repositories.audit_log_repository import AuditLogRepository
# from app.db.repositories.campus_card_repository import CampusCardRepository
# from app.db.repositories.leave_repository import LeaveRepository
# from app.db.repositories.pending_action_repository import PendingActionRepository
# from app.db.repositories.schedule_repository import ScheduleRepository
# from app.db.repositories.tool_execution_log_repository import ToolExecutionLogRepository
# from app.llm.base import BaseLlmProvider
# from app.llm.embeddings_provider import SimpleEmbeddingsProvider
# from app.rag.chunker import TextChunker
# from app.rag.document_loader import DocumentLoader
# from app.rag.knowledge_indexer import KnowledgeIndexer
# from app.rag.retriever import Retriever
# from app.rag.vector_store import InMemoryVectorStore
# from app.services.agent_session_service import AgentSessionService
# from app.services.audit_service import AuditService
# from app.services.campus_card_service import CampusCardService
# from app.services.leave_service import LeaveService
# from app.services.schedule_service import ScheduleService
# from app.services.tool_execution_log_service import ToolExecutionLogService

# router = APIRouter(prefix="/chat", tags=["chat"])


# def build_retriever() -> Retriever:
#     settings = get_settings()

#     embeddings_provider = SimpleEmbeddingsProvider()
#     vector_store = InMemoryVectorStore(embeddings_provider)
#     document_loader = DocumentLoader()
#     chunker = TextChunker(
#         chunk_size=settings.rag_chunk_size,
#         chunk_overlap=settings.rag_chunk_overlap,
#     )
#     indexer = KnowledgeIndexer(
#         document_loader=document_loader,
#         chunker=chunker,
#         vector_store=vector_store,
#     )
#     indexer.build_index(settings.knowledge_dir)

#     return Retriever(vector_store)


# def get_agent_session_service(
#     db: Session = Depends(get_db_dep),
#     llm_provider: BaseLlmProvider = Depends(get_llm_provider),
# ) -> AgentSessionService:
#     settings = get_settings()

#     agent_session_repository = AgentSessionRepository(db)
#     pending_action_repository = PendingActionRepository(db)
#     schedule_repository = ScheduleRepository(db)
#     campus_card_repository = CampusCardRepository(db)
#     leave_repository = LeaveRepository(db)
#     audit_log_repository = AuditLogRepository(db)
#     tool_execution_log_repository = ToolExecutionLogRepository(db)

#     schedule_service = ScheduleService(schedule_repository)
#     campus_card_service = CampusCardService(campus_card_repository)
#     leave_service = LeaveService(leave_repository)
#     audit_service = AuditService(audit_log_repository)
#     tool_execution_log_service = ToolExecutionLogService(tool_execution_log_repository)

#     retriever = build_retriever()

#     return AgentSessionService(
#         agent_session_repository=agent_session_repository,
#         pending_action_repository=pending_action_repository,
#         schedule_service=schedule_service,
#         campus_card_service=campus_card_service,
#         leave_service=leave_service,
#         audit_service=audit_service,
#         tool_execution_log_service=tool_execution_log_service,
#         llm_provider=llm_provider,
#         retriever=retriever,
#         rag_top_k=settings.rag_top_k,
#     )

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

@router.get("/tool-logs/{session_id}")
def get_tool_logs(
    session_id: int,
    current_user: User = Depends(get_current_user),
    agent_session_service: AgentSessionService = Depends(get_agent_session_service),
    tool_execution_log_service: ToolExecutionLogService = Depends(get_tool_execution_log_service),
) -> list[dict]:
    session = agent_session_service.get_user_session(
        session_id=session_id,
        user_id=current_user.id,
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    logs = tool_execution_log_service.list_by_session_id(session_id)

    results = []
    for item in logs:
        results.append(
            {
                "id": item.id,
                "session_id": item.session_id,
                "tool_name": item.tool_name,
                "input_json": item.input_json,
                "output_json": item.output_json,
                "status": item.status,
                "started_at": item.started_at.isoformat() if item.started_at else None,
                "finished_at": item.finished_at.isoformat() if item.finished_at else None,
            }
        )
    return results