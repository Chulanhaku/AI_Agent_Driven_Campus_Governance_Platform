from sqlalchemy.orm import Session, joinedload

from app.db.models import StudentCompletedCourse


class CompletedCourseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_passed_courses_by_user_id(
        self,
        *,
        user_id: int,
    ) -> list[StudentCompletedCourse]:
        return (
            self.db.query(StudentCompletedCourse)
            .options(joinedload(StudentCompletedCourse.course))
            .filter(
                StudentCompletedCourse.user_id == user_id,
                StudentCompletedCourse.passed.is_(True),
            )
            .all()
        )