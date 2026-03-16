from sqlalchemy.orm import Session

from app.db.models import Course


class CourseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_courses_by_semester(
        self,
        *,
        semester: str,
    ) -> list[Course]:
        return (
            self.db.query(Course)
            .filter(Course.semester == semester)
            .order_by(Course.id.asc())
            .all()
        )