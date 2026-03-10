from app.db.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, audit_log_repository: AuditLogRepository) -> None:
        self.audit_log_repository = audit_log_repository

    def record(
        self,
        *,
        user_id: int,
        action: str,
        target_type: str | None = None,
        target_id: int | None = None,
        detail_json: dict | None = None,
    ) -> None:
        try:
            self.audit_log_repository.create_log(
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                detail_json=detail_json,
            )
            self.audit_log_repository.commit()
        except Exception:
            self.audit_log_repository.rollback()
            raise

    def list_my_audit_logs(self, user_id: int) -> list:
        return self.audit_log_repository.list_by_user_id(user_id)