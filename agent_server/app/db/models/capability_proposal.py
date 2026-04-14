from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

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

    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="medium", nullable=False, index=True)
    activation_policy: Mapped[str] = mapped_column(
        String(20),
        default="review_required",
        nullable=False,
        index=True,
    )  # auto_activate / review_required / reject
    validation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False,
        index=True,
    )  # draft / validated / activated / rejected