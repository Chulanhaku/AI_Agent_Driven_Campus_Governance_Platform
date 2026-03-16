from sqlalchemy.orm import Session, joinedload

from app.db.models import CourseSection


class CourseSectionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_open_sections_by_semester(
        self,
        *,
        semester: str,
    ) -> list[CourseSection]:
        return (
            self.db.query(CourseSection)
            .options(joinedload(CourseSection.course))
            .filter(
                CourseSection.semester == semester,
                CourseSection.status == "open",
            )
            .order_by(CourseSection.course_id.asc(), CourseSection.id.asc())
            .all()
        )

    def list_open_sections_by_course_ids(
        self,
        *,
        semester: str,
        course_ids: list[int],
    ) -> list[CourseSection]:
        if not course_ids:
            return []

        return (
            self.db.query(CourseSection)
            .options(joinedload(CourseSection.course))
            .filter(
                CourseSection.semester == semester,
                CourseSection.status == "open",
                CourseSection.course_id.in_(course_ids),
            )
            .order_by(CourseSection.course_id.asc(), CourseSection.id.asc())
            .all()
        )