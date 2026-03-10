from sqlalchemy.orm import Session

from app.db.models import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_log(
        self,
        *,
        user_id: int,
        action: str,
        target_type: str | None = None,
        target_id: int | None = None,
        detail_json: dict | None = None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail_json=detail_json,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def list_by_user_id(self, user_id: int) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.id.desc())
            .all()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()