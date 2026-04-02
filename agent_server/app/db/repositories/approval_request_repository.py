from sqlalchemy.orm import Session, joinedload

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

    def get_by_id(
        self,
        *,
        request_id: int,
    ) -> ZeroFormApprovalRequest | None:
        return (
            self.db.query(ZeroFormApprovalRequest)
            .options(joinedload(ZeroFormApprovalRequest.template))
            .filter(ZeroFormApprovalRequest.id == request_id)
            .first()
        )

    def get_by_id_and_approver_user_id(
        self,
        *,
        request_id: int,
        approver_user_id: int,
    ) -> ZeroFormApprovalRequest | None:
        return (
            self.db.query(ZeroFormApprovalRequest)
            .options(joinedload(ZeroFormApprovalRequest.template))
            .filter(
                ZeroFormApprovalRequest.id == request_id,
                ZeroFormApprovalRequest.approver_user_id == approver_user_id,
            )
            .first()
        )

    def list_by_approver_user_id(
        self,
        *,
        approver_user_id: int,
        status: str | None = None,
        limit: int = 20,
    ) -> list[ZeroFormApprovalRequest]:
        query = (
            self.db.query(ZeroFormApprovalRequest)
            .options(joinedload(ZeroFormApprovalRequest.template))
            .filter(ZeroFormApprovalRequest.approver_user_id == approver_user_id)
            .order_by(ZeroFormApprovalRequest.id.desc())
        )

        if status:
            query = query.filter(ZeroFormApprovalRequest.status == status)

        return query.limit(limit).all()

    def update_status(
        self,
        *,
        item: ZeroFormApprovalRequest,
        status: str,
    ) -> ZeroFormApprovalRequest:
        item.status = status
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()