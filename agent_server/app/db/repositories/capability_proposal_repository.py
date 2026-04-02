from sqlalchemy.orm import Session

from app.db.models import CapabilityProposal


class CapabilityProposalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_proposal(
        self,
        *,
        session_id: int | None,
        user_id: int | None,
        trigger_message: str,
        proposal_type: str,
        capability_name: str,
        research_summary_json: dict | None,
        proposal_json: dict,
        status: str = "draft",
    ) -> CapabilityProposal:
        item = CapabilityProposal(
            session_id=session_id,
            user_id=user_id,
            trigger_message=trigger_message,
            proposal_type=proposal_type,
            capability_name=capability_name,
            research_summary_json=research_summary_json,
            proposal_json=proposal_json,
            status=status,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def get_by_id(
        self,
        *,
        proposal_id: int,
    ) -> CapabilityProposal | None:
        return (
            self.db.query(CapabilityProposal)
            .filter(CapabilityProposal.id == proposal_id)
            .first()
        )

    def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[CapabilityProposal]:
        return (
            self.db.query(CapabilityProposal)
            .order_by(CapabilityProposal.id.desc())
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        *,
        item: CapabilityProposal,
        status: str,
    ) -> CapabilityProposal:
        item.status = status
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
