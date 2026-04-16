from sqlalchemy import Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class GraduationRequirement(Base, TimestampMixin):
    __tablename__ = "graduation_requirements"
    __table_args__ = (
        UniqueConstraint(
            "department",
            "major",
            "grade",
            "requirement_code",
            name="uq_graduation_requirements_program_rule",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    requirement_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    major: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    grade: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    requirement_name: Mapped[str] = mapped_column(String(100), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    min_credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_course_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rule_json: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)