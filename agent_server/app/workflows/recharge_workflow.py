from app.db.models import PendingAction, User
from app.db.repositories.pending_action_repository import PendingActionRepository


class RechargeWorkflow:
    name = "recharge_workflow"

    def __init__(self, pending_action_repository: PendingActionRepository) -> None:
        self.pending_action_repository = pending_action_repository

    def create_pending_topup(
        self,
        *,
        current_user: User,
        session_id: int,
        amount: str,
    ) -> PendingAction:
        action = self.pending_action_repository.create_pending_action(
            session_id=session_id,
            user_id=current_user.id,
            action_type="campus_card_topup",
            payload_json={
                "amount": amount,
            },
            status="pending",
        )
        self.pending_action_repository.commit()
        return action