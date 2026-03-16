from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.db.models import CourseEnrollmentRequest, CourseEnrollmentRequestItem


class CourseEnrollmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_request(
        self,
        *,
        user_id: int,
        semester: str,
        request_type: str = "generated_plan_submit",
        status: str = "draft",
        plan_snapshot_json: dict | None = None,
        submitted_at: date | None = None,
    ) -> CourseEnrollmentRequest:
        request = CourseEnrollmentRequest(
            user_id=user_id,
            semester=semester,
            request_type=request_type,
            status=status,
            plan_snapshot_json=plan_snapshot_json,
            submitted_at=submitted_at,
        )
        self.db.add(request)
        self.db.flush()
        return request

    def create_request_item(
        self,
        *,
        request_id: int,
        course_id: int,
        section_id: int,
        priority: int,
        status: str = "pending",
    ) -> CourseEnrollmentRequestItem:
        item = CourseEnrollmentRequestItem(
            request_id=request_id,
            course_id=course_id,
            section_id=section_id,
            priority=priority,
            status=status,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def get_request_by_id_and_user_id(
        self,
        *,
        request_id: int,
        user_id: int,
    ) -> CourseEnrollmentRequest | None:
        return (
            self.db.query(CourseEnrollmentRequest)
            .options(joinedload(CourseEnrollmentRequest.items))
            .filter(
                CourseEnrollmentRequest.id == request_id,
                CourseEnrollmentRequest.user_id == user_id,
            )
            .first()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()