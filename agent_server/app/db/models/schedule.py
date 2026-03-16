from datetime import date, time
from sqlalchemy import JSON 
from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    course_name: Mapped[str] = mapped_column(String(100), nullable=False)
    teacher_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    credits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    semester: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # 新增：选课规划相关字段
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    course_type: Mapped[str] = mapped_column(String(30), default="elective", nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Numeric(6, 2), default=1.0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    offering_department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    schedule_entries = relationship(
        "ScheduleEntry",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    exam_schedules = relationship(
        "ExamSchedule",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    sections = relationship(
        "CourseSection",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CourseSection.id.asc()",
    )

    prerequisites = relationship(
        "CoursePrerequisite",
        back_populates="course",
        cascade="all, delete-orphan",
        foreign_keys="CoursePrerequisite.course_id",
    )

    prerequisite_for = relationship(
        "CoursePrerequisite",
        back_populates="prerequisite_course",
        cascade="all, delete-orphan",
        foreign_keys="CoursePrerequisite.prerequisite_course_id",
    )

    completed_by_students = relationship(
        "StudentCompletedCourse",
        back_populates="course",
        cascade="all, delete-orphan",
    )


class ScheduleEntry(Base, TimestampMixin):
    __tablename__ = "schedule_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 1~7
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    classroom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    week_range: Mapped[str] = mapped_column(String(50), nullable=False)
    semester: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    user = relationship("User", back_populates="schedule_entries")
    course = relationship("Course", back_populates="schedule_entries")


class ExamSchedule(Base, TimestampMixin):
    __tablename__ = "exam_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(nullable=False)
    end_time: Mapped[time] = mapped_column(nullable=False)
    exam_room: Mapped[str | None] = mapped_column(String(100), nullable=True)

    course = relationship("Course", back_populates="exam_schedules")


class CourseSection(Base, TimestampMixin):
    __tablename__ = "course_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    teacher_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    classroom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    semester: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False, index=True)

    course = relationship("Course", back_populates="sections")
    enrollment_request_items = relationship(
        "CourseEnrollmentRequestItem",
        back_populates="section",
        cascade="all, delete-orphan",
    )


class StudentCoursePlan(Base, TimestampMixin):
    __tablename__ = "student_course_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_semester: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    max_credits: Mapped[int] = mapped_column(Integer, default=18, nullable=False)
    #preferred_days_json: Mapped[list | None] = mapped_column(default=None, nullable=True)
    preferred_days_json: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    #avoid_days_json: Mapped[list | None] = mapped_column(default=None, nullable=True)
    avoid_days_json: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    
    avoid_morning: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avoid_evening: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    user = relationship("User", back_populates="student_course_plans")


class StudentCompletedCourse(Base, TimestampMixin):
    __tablename__ = "student_completed_courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    semester: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user = relationship("User", back_populates="completed_courses")
    course = relationship("Course", back_populates="completed_by_students")


class CoursePrerequisite(Base, TimestampMixin):
    __tablename__ = "course_prerequisites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prerequisite_course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_type: Mapped[str] = mapped_column(String(20), default="required", nullable=False, index=True)

    course = relationship(
        "Course",
        back_populates="prerequisites",
        foreign_keys=[course_id],
    )
    prerequisite_course = relationship(
        "Course",
        back_populates="prerequisite_for",
        foreign_keys=[prerequisite_course_id],
    )


class CourseEnrollmentRequest(Base, TimestampMixin):
    __tablename__ = "course_enrollment_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    semester: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(30), default="generated_plan_submit", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)
    #plan_snapshot_json: Mapped[dict | None] = mapped_column(default=None, nullable=True)
    plan_snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    submitted_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    user = relationship("User", back_populates="course_enrollment_requests")
    items = relationship(
        "CourseEnrollmentRequestItem",
        back_populates="request",
        cascade="all, delete-orphan",
        order_by="CourseEnrollmentRequestItem.priority.asc()",
    )


class CourseEnrollmentRequestItem(Base, TimestampMixin):
    __tablename__ = "course_enrollment_request_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("course_enrollment_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_id: Mapped[int] = mapped_column(
        ForeignKey("course_sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)

    request = relationship("CourseEnrollmentRequest", back_populates="items")
    section = relationship("CourseSection", back_populates="enrollment_request_items")