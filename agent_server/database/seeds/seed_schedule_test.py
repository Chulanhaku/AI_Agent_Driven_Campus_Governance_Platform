from datetime import time

from app.db.session import SessionLocal
from app.db.models import Course, ScheduleEntry, User


def seed_demo_schedule() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "student_demo").first()
        if user is None:
            raise RuntimeError("demo user not found, please run seed_demo_users first")

        semester = "2026-spring"

        course1 = db.query(Course).filter(Course.course_code == "CS101").first()
        if course1 is None:
            course1 = Course(
                course_code="CS101",
                course_name="Introduction to Programming",
                teacher_user_id=None,
                credits=4,
                semester=semester,
            )
            db.add(course1)
            db.flush()

        course2 = db.query(Course).filter(Course.course_code == "MATH201").first()
        if course2 is None:
            course2 = Course(
                course_code="MATH201",
                course_name="Discrete Mathematics",
                teacher_user_id=None,
                credits=3,
                semester=semester,
            )
            db.add(course2)
            db.flush()

        exists = (
            db.query(ScheduleEntry)
            .filter(ScheduleEntry.user_id == user.id, ScheduleEntry.semester == semester)
            .first()
        )
        if exists:
            print("demo schedule already exists")
            return

        entries = [
            ScheduleEntry(
                user_id=user.id,
                course_id=course1.id,
                weekday=1,
                start_time=time(8, 0),
                end_time=time(9, 40),
                classroom="A101",
                week_range="1-16",
                semester=semester,
            ),
            ScheduleEntry(
                user_id=user.id,
                course_id=course2.id,
                weekday=3,
                start_time=time(10, 0),
                end_time=time(11, 40),
                classroom="B202",
                week_range="1-16",
                semester=semester,
            ),
        ]

        db.add_all(entries)
        db.commit()
        print("seed demo schedule success")
    except Exception as exc:
        db.rollback()
        print(f"seed demo schedule failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_schedule()