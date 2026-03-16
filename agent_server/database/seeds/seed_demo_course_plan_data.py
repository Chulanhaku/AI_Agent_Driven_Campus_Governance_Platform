from app.db.models import (
    Course,
    CoursePrerequisite,
    CourseSection,
    StudentCompletedCourse,
    StudentCoursePlan,
    User,
)
from app.db.session import SessionLocal


def seed_demo_course_plan_data() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "student_demo").first()
        if user is None:
            raise RuntimeError("demo user not found, please run seed_demo_users first")

        semester = "2026-spring"

        exists = db.query(StudentCoursePlan).filter(
            StudentCoursePlan.user_id == user.id,
            StudentCoursePlan.target_semester == semester,
        ).first()
        if exists:
            print("demo course plan data already exists")
            return

        # ---------------------------
        # 1. 创建课程
        # ---------------------------
        course_programming = Course(
            course_code="CS101",
            course_name="Introduction to Programming",
            credits=4,
            semester=semester,
            capacity=120,
            enrolled_count=80,
            course_type="required",
            weight=9.5,
            is_required=True,
            offering_department="Computer Science",
        )

        course_discrete = Course(
            course_code="CS102",
            course_name="Discrete Mathematics",
            credits=3,
            semester=semester,
            capacity=100,
            enrolled_count=65,
            course_type="required",
            weight=8.8,
            is_required=True,
            offering_department="Computer Science",
        )

        course_data_structure = Course(
            course_code="CS201",
            course_name="Data Structures",
            credits=4,
            semester=semester,
            capacity=80,
            enrolled_count=40,
            course_type="required",
            weight=9.7,
            is_required=True,
            offering_department="Computer Science",
        )

        course_database = Course(
            course_code="CS202",
            course_name="Database Systems",
            credits=3,
            semester=semester,
            capacity=90,
            enrolled_count=35,
            course_type="elective",
            weight=8.0,
            is_required=False,
            offering_department="Computer Science",
        )

        course_ai_intro = Course(
            course_code="CS203",
            course_name="Introduction to AI",
            credits=3,
            semester=semester,
            capacity=70,
            enrolled_count=30,
            course_type="elective",
            weight=8.6,
            is_required=False,
            offering_department="Computer Science",
        )

        course_english = Course(
            course_code="GE101",
            course_name="College English",
            credits=2,
            semester=semester,
            capacity=150,
            enrolled_count=110,
            course_type="general",
            weight=6.5,
            is_required=False,
            offering_department="General Education",
        )

        db.add_all([
            course_programming,
            course_discrete,
            course_data_structure,
            course_database,
            course_ai_intro,
            course_english,
        ])
        db.flush()

        # ---------------------------
        # 2. 创建教学班 section
        # ---------------------------
        sections = [
            CourseSection(
                course_id=course_programming.id,
                section_code="CS101-A",
                weekday=1,
                start_time="08:00:00",
                end_time="09:40:00",
                classroom="A101",
                capacity=60,
                enrolled_count=40,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_programming.id,
                section_code="CS101-B",
                weekday=2,
                start_time="10:00:00",
                end_time="11:40:00",
                classroom="A102",
                capacity=60,
                enrolled_count=40,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_discrete.id,
                section_code="CS102-A",
                weekday=3,
                start_time="10:00:00",
                end_time="11:40:00",
                classroom="B202",
                capacity=50,
                enrolled_count=30,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_discrete.id,
                section_code="CS102-B",
                weekday=4,
                start_time="08:00:00",
                end_time="09:40:00",
                classroom="B203",
                capacity=50,
                enrolled_count=35,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_data_structure.id,
                section_code="CS201-A",
                weekday=1,
                start_time="14:00:00",
                end_time="15:40:00",
                classroom="C301",
                capacity=40,
                enrolled_count=15,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_data_structure.id,
                section_code="CS201-B",
                weekday=5,
                start_time="10:00:00",
                end_time="11:40:00",
                classroom="C302",
                capacity=40,
                enrolled_count=25,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_database.id,
                section_code="CS202-A",
                weekday=2,
                start_time="14:00:00",
                end_time="15:40:00",
                classroom="D201",
                capacity=45,
                enrolled_count=20,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_ai_intro.id,
                section_code="CS203-A",
                weekday=3,
                start_time="14:00:00",
                end_time="15:40:00",
                classroom="D202",
                capacity=35,
                enrolled_count=15,
                semester=semester,
                status="open",
            ),
            CourseSection(
                course_id=course_english.id,
                section_code="GE101-A",
                weekday=4,
                start_time="14:00:00",
                end_time="15:40:00",
                classroom="E101",
                capacity=80,
                enrolled_count=60,
                semester=semester,
                status="open",
            ),
        ]

        from datetime import time

        def parse_time(value: str) -> time:
            hh, mm, ss = value.split(":")
            return time(int(hh), int(mm), int(ss))

        for item in sections:
            item.start_time = parse_time(item.start_time)  # type: ignore[arg-type]
            item.end_time = parse_time(item.end_time)      # type: ignore[arg-type]

        db.add_all(sections)
        db.flush()

        # ---------------------------
        # 3. 创建学生修读计划
        # ---------------------------
        student_plan = StudentCoursePlan(
            user_id=user.id,
            plan_name="2026 春季默认修读计划",
            target_semester=semester,
            max_credits=12,
            preferred_days_json=[1, 2, 3, 4],
            avoid_days_json=[5],
            avoid_morning=False,
            avoid_evening=True,
            status="active",
        )
        db.add(student_plan)
        db.flush()

        # ---------------------------
        # 4. 创建已修课程
        # 让 student_demo 已经修过 CS101
        # ---------------------------
        completed_programming = StudentCompletedCourse(
            user_id=user.id,
            course_id=course_programming.id,
            grade="A",
            passed=True,
            semester="2025-fall",
        )
        db.add(completed_programming)
        db.flush()

        # ---------------------------
        # 5. 创建先修关系
        # Data Structures 需要 CS101
        # Introduction to AI 推荐先修 Data Structures
        # ---------------------------
        prereq_1 = CoursePrerequisite(
            course_id=course_data_structure.id,
            prerequisite_course_id=course_programming.id,
            rule_type="required",
        )

        prereq_2 = CoursePrerequisite(
            course_id=course_ai_intro.id,
            prerequisite_course_id=course_data_structure.id,
            rule_type="required",
        )

        db.add_all([prereq_1, prereq_2])

        db.commit()
        print("seed demo course plan data success")

    except Exception as exc:
        db.rollback()
        print(f"seed demo course plan data failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_course_plan_data()