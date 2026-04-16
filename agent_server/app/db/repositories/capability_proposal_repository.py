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
        confidence_score: float = 0.0,
        risk_level: str = "medium",
        activation_policy: str = "review_required",
        validation_reason: str | None = None,
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
            confidence_score=confidence_score,
            risk_level=risk_level,
            activation_policy=activation_policy,
            validation_reason=validation_reason,
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

    def list_activated(
        self,
        *,
        limit: int = 500,
    ) -> list[CapabilityProposal]:
        return (
            self.db.query(CapabilityProposal)
            .filter(CapabilityProposal.status == "activated")
            .order_by(CapabilityProposal.id.asc())
            .limit(limit)
            .all()
        )

    def list_validated(
        self,
        *,
        limit: int = 100,
    ) -> list[CapabilityProposal]:
        return (
            self.db.query(CapabilityProposal)
            .filter(CapabilityProposal.status == "validated")
            .order_by(CapabilityProposal.id.asc())
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

    def update_decision(
        self,
        *,
        item: CapabilityProposal,
        status: str,
        confidence_score: float,
        risk_level: str,
        activation_policy: str,
        validation_reason: str | None,
    ) -> CapabilityProposal:
        item.status = status
        item.confidence_score = confidence_score
        item.risk_level = risk_level
        item.activation_policy = activation_policy
        item.validation_reason = validation_reason
        self.db.flush()
        return item

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()