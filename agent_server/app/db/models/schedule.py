# from datetime import date, time
# from sqlalchemy import String, Integer, ForeignKey, Date, Time
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from app.db.base import Base, TimestampMixin


# class Course(Base, TimestampMixin):
#     __tablename__ = "courses"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     course_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
#     course_name: Mapped[str] = mapped_column(String(100), nullable=False)
#     teacher_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
#     credits: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     semester: Mapped[str] = mapped_column(String(50), nullable=False)

#     schedule_entries = relationship("ScheduleEntry", back_populates="course")
#     exam_schedules = relationship("ExamSchedule", back_populates="course")


# class ScheduleEntry(Base, TimestampMixin):
#     __tablename__ = "schedule_entries"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
#     course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
#     weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 1~7
#     start_time: Mapped[time] = mapped_column(Time, nullable=False)
#     end_time: Mapped[time] = mapped_column(Time, nullable=False)
#     classroom: Mapped[str | None] = mapped_column(String(100), nullable=True)
#     week_range: Mapped[str] = mapped_column(String(50), nullable=False)
#     semester: Mapped[str] = mapped_column(String(50), nullable=False)

#     user = relationship("User", back_populates="schedule_entries")
#     course = relationship("Course", back_populates="schedule_entries")


# class ExamSchedule(Base, TimestampMixin):
#     __tablename__ = "exam_schedules"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
#     exam_date: Mapped[date] = mapped_column(Date, nullable=False)
#     start_time: Mapped[time] = mapped_column(Time, nullable=False)
#     end_time: Mapped[time] = mapped_column(Time, nullable=False)
#     exam_room: Mapped[str | None] = mapped_column(String(100), nullable=True)

#     course = relationship("Course", back_populates="exam_schedules")

from datetime import date, time

from sqlalchemy import Date, ForeignKey, Integer, String, Time
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