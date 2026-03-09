# from sqlalchemy import String, ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from app.db.base import Base, TimestampMixin


# class StudentProfile(Base, TimestampMixin):
#     __tablename__ = "student_profiles"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
#     student_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
#     department: Mapped[str] = mapped_column(String(100), nullable=False)
#     major: Mapped[str | None] = mapped_column(String(100), nullable=True)
#     class_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
#     grade: Mapped[str | None] = mapped_column(String(20), nullable=True)

#     user = relationship("User", back_populates="student_profile")


# class TeacherProfile(Base, TimestampMixin):
#     __tablename__ = "teacher_profiles"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
#     teacher_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
#     department: Mapped[str] = mapped_column(String(100), nullable=False)
#     title: Mapped[str | None] = mapped_column(String(100), nullable=True)
#     office: Mapped[str | None] = mapped_column(String(100), nullable=True)

#     user = relationship("User", back_populates="teacher_profile")

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    student_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)
    class_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user = relationship("User", back_populates="student_profile")


class TeacherProfile(Base, TimestampMixin):
    __tablename__ = "teacher_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    teacher_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    office: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user = relationship("User", back_populates="teacher_profile")