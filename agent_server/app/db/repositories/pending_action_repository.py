from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import PendingAction


class PendingActionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_pending_action(
        self,
        *,
        session_id: int,
        user_id: int,
        action_type: str,
        payload_json: dict,
        status: str = "pending",
        expires_at: datetime | None = None,
    ) -> PendingAction:
        action = PendingAction(
            session_id=session_id,
            user_id=user_id,
            action_type=action_type,
            payload_json=payload_json,
            status=status,
            expires_at=expires_at,
        )
        self.db.add(action)
        self.db.flush()
        return action

    def get_by_id_and_user_id(
        self,
        action_id: int,
        user_id: int,
    ) -> PendingAction | None:
        return (
            self.db.query(PendingAction)
            .filter(
                PendingAction.id == action_id,
                PendingAction.user_id == user_id,
            )
            .first()
        )

    def update_status(
        self,
        *,
        action: PendingAction,
        status: str,
    ) -> PendingAction:
        action.status = status
        self.db.flush()
        return action

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()