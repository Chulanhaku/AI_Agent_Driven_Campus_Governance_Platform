from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ApprovalTemplate(Base, TimestampMixin):
    __tablename__ = "approval_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    approval_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_fields_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    approver_role_code: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    requests = relationship(
        "ZeroFormApprovalRequest",
        back_populates="template",
        cascade="all, delete-orphan",
    )


class ZeroFormApprovalRequest(Base, TimestampMixin):
    __tablename__ = "zero_form_approval_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    template_id: Mapped[int] = mapped_column(
        ForeignKey("approval_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approval_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    form_data_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    approver_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )  # draft / pending / approved / rejected / cancelled

    user = relationship(
        "User",
        back_populates="zero_form_approval_requests",
        foreign_keys=[user_id],
    )
    template = relationship(
        "ApprovalTemplate",
        back_populates="requests",
    )