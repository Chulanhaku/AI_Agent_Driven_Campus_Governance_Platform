from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_dep
from app.db.models import User
from app.db.repositories.audit_log_repository import AuditLogRepository
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


def get_audit_service(db: Session = Depends(get_db_dep)) -> AuditService:
    repository = AuditLogRepository(db)
    return AuditService(repository)


@router.get("/me")
def list_my_audit_logs(
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service),
) -> list[dict]:
    items = audit_service.list_my_audit_logs(user_id=current_user.id)

    results = []
    for item in items:
        results.append(
            {
                "id": item.id,
                "action": item.action,
                "target_type": item.target_type,
                "target_id": item.target_id,
                "detail_json": item.detail_json,
                "created_at": item.created_at.isoformat(),
            }
        )
    return results