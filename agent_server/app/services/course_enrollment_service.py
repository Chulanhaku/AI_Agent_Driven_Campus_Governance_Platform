from datetime import date

from app.db.repositories.course_enrollment_repository import CourseEnrollmentRepository


class CourseEnrollmentService:
    def __init__(
        self,
        course_enrollment_repository: CourseEnrollmentRepository,
    ) -> None:
        self.course_enrollment_repository = course_enrollment_repository

    def submit_generated_plan(
        self,
        *,
        user_id: int,
        semester: str,
        selected_plan: dict,
    ) -> dict:
        try:
            request = self.course_enrollment_repository.create_request(
                user_id=user_id,
                semester=semester,
                request_type="generated_plan_submit",
                status="submitted",
                plan_snapshot_json=selected_plan,
                submitted_at=date.today(),
            )

            for idx, item in enumerate(selected_plan.get("items", []), start=1):
                self.course_enrollment_repository.create_request_item(
                    request_id=request.id,
                    course_id=item["course_id"],
                    section_id=item["section_id"],
                    priority=idx,
                    status="submitted",
                )

            self.course_enrollment_repository.commit()

            return {
                "success": True,
                "request_id": request.id,
                "semester": semester,
                "submitted_course_count": len(selected_plan.get("items", [])),
                "status": request.status,
            }
        except Exception:
            self.course_enrollment_repository.rollback()
            raise