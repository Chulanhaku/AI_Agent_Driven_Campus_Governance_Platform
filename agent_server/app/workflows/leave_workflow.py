from app.db.models import PendingAction, User
from app.db.repositories.pending_action_repository import PendingActionRepository


class LeaveWorkflow:
    name = "leave_workflow"

    def __init__(self, pending_action_repository: PendingActionRepository) -> None:
        self.pending_action_repository = pending_action_repository

    def create_pending_leave_request(
        self,
        *,
        current_user: User,
        session_id: int,
        days: int,
        reason: str,
        leave_type: str = "sick",
    ) -> PendingAction:
        action = self.pending_action_repository.create_pending_action(
            session_id=session_id,
            user_id=current_user.id,
            action_type="leave_create",
            payload_json={
                "days": days,
                "reason": reason,
                "leave_type": leave_type,
            },
            status="pending",
        )
        self.pending_action_repository.commit()
        return action