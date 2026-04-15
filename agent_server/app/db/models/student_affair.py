from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class StudentRewardPunishmentRecord(Base, TimestampMixin):
    __tablename__ = "student_reward_punishment_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    record_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # reward / punishment
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # scholarship / competition / discipline
    level: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    score_delta: Mapped[int] = mapped_column(default=0, nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    issuing_unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="effective", nullable=False, index=True)

    user = relationship("User")