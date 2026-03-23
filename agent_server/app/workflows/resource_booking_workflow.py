from app.db.models import PendingAction, User
from app.db.repositories.pending_action_repository import PendingActionRepository


class ResourceBookingWorkflow:
    name = "resource_booking_workflow"

    def __init__(self, pending_action_repository: PendingActionRepository) -> None:
        self.pending_action_repository = pending_action_repository

    def create_pending_booking(
        self,
        *,
        current_user: User,
        session_id: int,
        resource_id: int,
        booking_type: str,
        start_time: str,
        end_time: str,
        selected_resource: dict,
        selected_resource_index: int,
    ) -> PendingAction:
        action = self.pending_action_repository.create_pending_action(
            session_id=session_id,
            user_id=current_user.id,
            action_type="resource_booking_submit",
            payload_json={
                "resource_id": resource_id,
                "booking_type": booking_type,
                "start_time": start_time,
                "end_time": end_time,
                "selected_resource": selected_resource,
                "selected_resource_index": selected_resource_index,
            },
            status="pending",
        )
        self.pending_action_repository.commit()
        return action