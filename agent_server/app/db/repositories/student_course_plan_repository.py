from sqlalchemy.orm import Session

from app.db.models import StudentCoursePlan


class StudentCoursePlanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_plan_by_user_id_and_semester(
        self,
        *,
        user_id: int,
        semester: str,
    ) -> StudentCoursePlan | None:
        return (
            self.db.query(StudentCoursePlan)
            .filter(
                StudentCoursePlan.user_id == user_id,
                StudentCoursePlan.target_semester == semester,
                StudentCoursePlan.status == "active",
            )
            .first()
        )