from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DynamicToolDefinition(Base, TimestampMixin):
    __tablename__ = "dynamic_tool_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_proposal_id: Mapped[int | None] = mapped_column(
        ForeignKey("capability_proposals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    tool_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    primary_intent: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tool_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # db_query / web_search / composed / template
    description: Mapped[str] = mapped_column(Text, nullable=False)

    input_schema_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    execution_config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
    )  # active / disabled


class DynamicPlanDefinition(Base, TimestampMixin):
    __tablename__ = "dynamic_plan_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_proposal_id: Mapped[int | None] = mapped_column(
        ForeignKey("capability_proposals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    capability_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    primary_intent: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
    )  # active / disabled