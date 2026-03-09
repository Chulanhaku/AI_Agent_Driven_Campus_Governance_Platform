from sqlalchemy.orm import Session, joinedload

from app.db.models import ScheduleEntry


class ScheduleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user_id(
        self,
        user_id: int,
        semester: str | None = None,
        weekday: int | None = None,
    ) -> list[ScheduleEntry]:
        query = (
            self.db.query(ScheduleEntry)
            .options(joinedload(ScheduleEntry.course))
            .filter(ScheduleEntry.user_id == user_id)
        )

        if semester:
            query = query.filter(ScheduleEntry.semester == semester)

        if weekday:
            query = query.filter(ScheduleEntry.weekday == weekday)

        return query.order_by(
            ScheduleEntry.weekday.asc(),
            ScheduleEntry.start_time.asc(),
        ).all()