from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db.repositories.capability_proposal_repository import CapabilityProposalRepository
from app.api.deps import get_capability_registry
from app.self_iteration.capability_registry import CapabilityRegistry


router = APIRouter(prefix="/capabilities", tags=["capabilities"])


@router.get("/registry")
def get_capability_registry_snapshot(
    capability_registry: CapabilityRegistry = Depends(get_capability_registry),
) -> dict:
    return capability_registry.snapshot()


@router.get("/proposals")
def list_capability_proposals(
    db: Session = Depends(get_db_dep),
) -> list[dict]:
    repository = CapabilityProposalRepository(db)
    items = repository.list_recent(limit=50)

    return [
        {
            "id": item.id,
            "session_id": item.session_id,
            "user_id": item.user_id,
            "trigger_message": item.trigger_message,
            "proposal_type": item.proposal_type,
            "capability_name": item.capability_name,
            "research_summary_json": item.research_summary_json,
            "proposal_json": item.proposal_json,
            "status": item.status,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]