from app.db.models import PendingAction, User
from app.db.repositories.pending_action_repository import PendingActionRepository


class ZeroFormApprovalWorkflow:
    name = "zero_form_approval_workflow"

    def __init__(self, pending_action_repository: PendingActionRepository) -> None:
        self.pending_action_repository = pending_action_repository

    def create_pending_submit(
        self,
        *,
        current_user: User,
        session_id: int,
        approval_type: str,
        template_id: int,
        approver_user_id: int | None,
        form_data: dict,
    ) -> PendingAction:
        action = self.pending_action_repository.create_pending_action(
            session_id=session_id,
            user_id=current_user.id,
            action_type="zero_form_approval_submit",
            payload_json={
                "approval_type": approval_type,
                "template_id": template_id,
                "approver_user_id": approver_user_id,
                "form_data": form_data,
            },
            status="pending",
        )
        self.pending_action_repository.commit()
        return action