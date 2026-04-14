from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ToolSpecArtifact(Base, TimestampMixin):
    __tablename__ = "tool_spec_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("capability_proposals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    capability_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(30), default="tool_stub", nullable=False, index=True)
    content_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    code_text: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        default="generated",
        nullable=False,
        index=True,
    )  # generated / reviewed / implemented / rejected

    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    implemented_tool_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    implemented_module_path: Mapped[str | None] = mapped_column(String(500), nullable=True)