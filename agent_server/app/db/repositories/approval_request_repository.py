from sqlalchemy.orm import Session

from app.db.models import ZeroFormApprovalRequest


class ApprovalRequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_request(
        self,
        *,
        user_id: int,
        template_id: int,
        approval_type: str,
        form_data_json: dict,
        approver_user_id: int | None,
        status: str = "pending",
    ) -> ZeroFormApprovalRequest:
        item = ZeroFormApprovalRequest(
            user_id=user_id,
            template_id=template_id,
            approval_type=approval_type,
            form_data_json=form_data_json,
            approver_user_id=approver_user_id,
            status=status,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()