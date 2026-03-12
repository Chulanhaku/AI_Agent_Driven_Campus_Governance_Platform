from app.db.models import AgentSessionMemory
from app.db.repositories.agent_session_memory_repository import AgentSessionMemoryRepository


class AgentMemoryService:
    def __init__(self, memory_repository: AgentSessionMemoryRepository) -> None:
        self.memory_repository = memory_repository

    def get_session_memory(self, session_id: int) -> AgentSessionMemory | None:
        return self.memory_repository.get_by_session_id(session_id)

    def save_memory_snapshot(
        self,
        *,
        session_id: int,
        summary_text: str | None,
        current_intent: str | None,
        slot_snapshot_json: dict | None,
    ) -> AgentSessionMemory:
        try:
            memory = self.memory_repository.create_or_update(
                session_id=session_id,
                summary_text=summary_text,
                current_intent=current_intent,
                slot_snapshot_json=slot_snapshot_json,
            )
            self.memory_repository.commit()
            return memory
        except Exception:
            self.memory_repository.rollback()
            raise