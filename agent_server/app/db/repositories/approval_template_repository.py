from sqlalchemy.orm import Session

from app.db.models import ApprovalTemplate


class ApprovalTemplateRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_by_approval_type(
        self,
        *,
        approval_type: str,
    ) -> ApprovalTemplate | None:
        return (
            self.db.query(ApprovalTemplate)
            .filter(
                ApprovalTemplate.approval_type == approval_type,
                ApprovalTemplate.status == "active",
            )
            .first()
        )