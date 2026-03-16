from app.db.session import SessionLocal
from app.db.repositories.completed_course_repository import CompletedCourseRepository
from app.db.repositories.course_prerequisite_repository import CoursePrerequisiteRepository
from app.db.repositories.course_section_repository import CourseSectionRepository
from app.db.repositories.student_course_plan_repository import StudentCoursePlanRepository
from app.services.course_plan_service import CoursePlanService


def main() -> None:
    db = SessionLocal()
    try:
        service = CoursePlanService(
            course_section_repository=CourseSectionRepository(db),
            student_course_plan_repository=StudentCoursePlanRepository(db),
            completed_course_repository=CompletedCourseRepository(db),
            course_prerequisite_repository=CoursePrerequisiteRepository(db),
        )

        result = service.generate_candidate_plans(
            user_id=1,
            semester="2026-spring",
            max_plan_count=3,
        )
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()