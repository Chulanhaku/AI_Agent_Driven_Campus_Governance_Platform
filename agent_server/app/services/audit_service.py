from app.db.repositories.audit_log_repository import AuditLogRepository
from decimal import Decimal
from datetime import date, datetime
from enum import Enum


def to_json_safe(value):
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Decimal):
        return str(value)  # 审计日志里建议保留精度

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {
            str(k): to_json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(v) for v in value]

    if hasattr(value, "__dict__"):
        return {
            k: to_json_safe(v)
            for k, v in vars(value).items()
            if not k.startswith("_")
        }

    return str(value)

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
            safe_detail_json = to_json_safe(detail_json)
            self.audit_log_repository.create_log(
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                detail_json=safe_detail_json,
            )
            self.audit_log_repository.commit()
        except Exception:
            self.audit_log_repository.rollback()
            raise

    def list_my_audit_logs(self, user_id: int) -> list:
        return self.audit_log_repository.list_by_user_id(user_id)