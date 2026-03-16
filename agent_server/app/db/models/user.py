from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role = relationship("Role", back_populates="users")

    student_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    teacher_profile = relationship(
        "TeacherProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    schedule_entries = relationship(
        "ScheduleEntry",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    agent_sessions = relationship(
        "AgentSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    campus_card_account = relationship(
        "CampusCardAccount",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    pending_actions = relationship(
        "PendingAction",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    leave_requests = relationship(
        "LeaveRequest",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    student_course_plans = relationship(
        "StudentCoursePlan",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    completed_courses = relationship(
        "StudentCompletedCourse",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    course_enrollment_requests = relationship(
        "CourseEnrollmentRequest",
        back_populates="user",
        cascade="all, delete-orphan",
    )