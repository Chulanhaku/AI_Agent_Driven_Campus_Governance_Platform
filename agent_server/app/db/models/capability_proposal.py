from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class CapabilityProposal(Base, TimestampMixin):
    __tablename__ = "capability_proposals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True, index=True)

    trigger_message: Mapped[str] = mapped_column(Text, nullable=False)
    proposal_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    capability_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    research_summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    proposal_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False,
        index=True,
    )