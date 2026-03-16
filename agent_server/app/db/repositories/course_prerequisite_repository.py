from sqlalchemy.orm import Session

from app.db.models import CoursePrerequisite


class CoursePrerequisiteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[CoursePrerequisite]:
        return (
            self.db.query(CoursePrerequisite)
            .order_by(CoursePrerequisite.id.asc())
            .all()
        )