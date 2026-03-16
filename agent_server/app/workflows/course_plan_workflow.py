from app.db.models import PendingAction, User
from app.db.repositories.pending_action_repository import PendingActionRepository


class CoursePlanWorkflow:
    name = "course_plan_workflow"

    def __init__(self, pending_action_repository: PendingActionRepository) -> None:
        self.pending_action_repository = pending_action_repository

    def create_pending_submit(
        self,
        *,
        current_user: User,
        session_id: int,
        semester: str,
        selected_plan: dict,
        selected_plan_index: int,
    ) -> PendingAction:
        action = self.pending_action_repository.create_pending_action(
            session_id=session_id,
            user_id=current_user.id,
            action_type="course_plan_submit",
            payload_json={
                "semester": semester,
                "selected_plan_index": selected_plan_index,
                "selected_plan": selected_plan,
            },
            status="pending",
        )
        self.pending_action_repository.commit()
        return action