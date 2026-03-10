from sqlalchemy.orm import Session, joinedload

from app.db.models import AgentMessage, AgentSession


class AgentSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(
        self,
        user_id: int,
        title: str | None = None,
    ) -> AgentSession:
        session = AgentSession(
            user_id=user_id,
            title=title,
            status="active",
        )
        self.db.add(session)
        self.db.flush()
        return session

    def get_session_by_id(self, session_id: int) -> AgentSession | None:
        return (
            self.db.query(AgentSession)
            .options(joinedload(AgentSession.messages))
            .filter(AgentSession.id == session_id)
            .first()
        )

    def get_session_by_id_and_user_id(
        self,
        session_id: int,
        user_id: int,
    ) -> AgentSession | None:
        return (
            self.db.query(AgentSession)
            .options(joinedload(AgentSession.messages))
            .filter(
                AgentSession.id == session_id,
                AgentSession.user_id == user_id,
            )
            .first()
        )

    def add_message(
        self,
        session_id: int,
        role: str,
        content: str,
        message_type: str = "text",
    ) -> AgentMessage:
        message = AgentMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_type=message_type,
        )
        self.db.add(message)
        self.db.flush()
        return message

    def list_messages_by_session_id(
        self,
        session_id: int,
    ) -> list[AgentMessage]:
        return (
            self.db.query(AgentMessage)
            .filter(AgentMessage.session_id == session_id)
            .order_by(AgentMessage.id.asc())
            .all()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()