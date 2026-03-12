from sqlalchemy.orm import Session

from app.db.models import AgentSessionMemory


class AgentSessionMemoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_session_id(self, session_id: int) -> AgentSessionMemory | None:
        return (
            self.db.query(AgentSessionMemory)
            .filter(AgentSessionMemory.session_id == session_id)
            .first()
        )

    def create(
        self,
        *,
        session_id: int,
        summary_text: str | None = None,
        current_intent: str | None = None,
        slot_snapshot_json: dict | None = None,
    ) -> AgentSessionMemory:
        memory = AgentSessionMemory(
            session_id=session_id,
            summary_text=summary_text,
            current_intent=current_intent,
            slot_snapshot_json=slot_snapshot_json,
        )
        self.db.add(memory)
        self.db.flush()
        return memory

    def create_or_update(
        self,
        *,
        session_id: int,
        summary_text: str | None = None,
        current_intent: str | None = None,
        slot_snapshot_json: dict | None = None,
    ) -> AgentSessionMemory:
        memory = self.get_by_session_id(session_id)

        if memory is None:
            memory = self.create(
                session_id=session_id,
                summary_text=summary_text,
                current_intent=current_intent,
                slot_snapshot_json=slot_snapshot_json,
            )
            return memory

        memory.summary_text = summary_text
        memory.current_intent = current_intent
        memory.slot_snapshot_json = slot_snapshot_json
        self.db.flush()
        return memory

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()