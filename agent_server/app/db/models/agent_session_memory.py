from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class AgentSessionMemory(Base, TimestampMixin):
    __tablename__ = "agent_session_memories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("agent_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_intent: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    slot_snapshot_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    session = relationship("AgentSession", back_populates="memory")