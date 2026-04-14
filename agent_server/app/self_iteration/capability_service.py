from app.self_iteration.capability_designer import CapabilityDesigner
from app.self_iteration.capability_detector import CapabilityDetector
from app.self_iteration.capability_researcher import CapabilityResearcher
from app.self_iteration.capability_validator import CapabilityValidator
from app.self_iteration.capability_loader import CapabilityLoader
from app.self_iteration.capability_policy import CapabilityPolicy
from app.db.repositories.capability_proposal_repository import CapabilityProposalRepository


class CapabilityService:
    def __init__(
        self,
        capability_proposal_repository: CapabilityProposalRepository,
        capability_detector: CapabilityDetector,
        capability_researcher: CapabilityResearcher,
        capability_designer: CapabilityDesigner,
        capability_validator: CapabilityValidator,
        capability_loader: CapabilityLoader,
        capability_policy: CapabilityPolicy,
    ) -> None:
        self.capability_proposal_repository = capability_proposal_repository
        self.capability_detector = capability_detector
        self.capability_researcher = capability_researcher
        self.capability_designer = capability_designer
        self.capability_validator = capability_validator
        self.capability_loader = capability_loader
        self.capability_policy = capability_policy

    def try_propose_from_fallback(
        self,
        *,
        session_id: int | None,
        user_id: int | None,
        user_message: str,
        memory_summary: str | None,
    ) -> dict | None:
        if not self.capability_detector.should_propose(user_message=user_message):
            return None

        research_summary = self.capability_researcher.research(
            user_message=user_message,
        )

        proposal = self.capability_designer.design(
            user_message=user_message,
            research_summary=research_summary,
            memory_summary=memory_summary,
        )

        capability_name = proposal.get("capability_name") or "unnamed_capability"
        proposal_type = proposal.get("proposal_type") or "tool_spec"

        try:
            validation_result = self.capability_validator.validate(proposal=proposal)
            policy_result = self.capability_policy.decide(
                proposal=proposal,
                validation_result=validation_result,
            )

            item = self.capability_proposal_repository.create_proposal(
                session_id=session_id,
                user_id=user_id,
                trigger_message=user_message,
                proposal_type=proposal_type,
                capability_name=capability_name,
                research_summary_json=research_summary,
                proposal_json=proposal,
                status=policy_result["final_status"],
                confidence_score=validation_result["confidence_score"],
                risk_level=validation_result["risk_level"],
                activation_policy=policy_result["activation_policy"],
                validation_reason=policy_result["reason"],
            )

            activation_result = None
            if policy_result["final_status"] == "activated":
                activation_result = self.capability_loader.load(proposal=proposal)

            self.capability_proposal_repository.commit()

            return {
                "success": True,
                "proposal_id": item.id,
                "proposal_type": item.proposal_type,
                "capability_name": item.capability_name,
                "proposal": proposal,
                "validation_result": validation_result,
                "policy_result": policy_result,
                "activation_result": activation_result,
                "status": item.status,
                "confidence_score": item.confidence_score,
                "risk_level": item.risk_level,
                "activation_policy": item.activation_policy,
            }
        except Exception:
            self.capability_proposal_repository.rollback()
            raise

    def list_validated_proposals(
        self,
        *,
        limit: int = 100,
    ) -> list[dict]:
        items = self.capability_proposal_repository.list_validated(limit=limit)
        return [
            {
                "id": item.id,
                "session_id": item.session_id,
                "user_id": item.user_id,
                "trigger_message": item.trigger_message,
                "proposal_type": item.proposal_type,
                "capability_name": item.capability_name,
                "proposal_json": item.proposal_json,
                "confidence_score": item.confidence_score,
                "risk_level": item.risk_level,
                "activation_policy": item.activation_policy,
                "validation_reason": item.validation_reason,
                "status": item.status,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ]

    def approve_validated_proposal(
        self,
        *,
        proposal_id: int,
    ) -> dict:
        item = self.capability_proposal_repository.get_by_id(proposal_id=proposal_id)
        if item is None:
            raise ValueError("Capability proposal not found")

        if item.status != "validated":
            raise ValueError("Only validated proposal can be approved")

        try:
            activation_result = self.capability_loader.load(
                proposal=item.proposal_json,
            )

            self.capability_proposal_repository.update_status(
                item=item,
                status="activated",
            )
            self.capability_proposal_repository.commit()

            return {
                "success": True,
                "proposal_id": item.id,
                "capability_name": item.capability_name,
                "proposal_type": item.proposal_type,
                "status": item.status,
                "activation_result": activation_result,
            }
        except Exception:
            self.capability_proposal_repository.rollback()
            raise

    def reject_validated_proposal(
        self,
        *,
        proposal_id: int,
    ) -> dict:
        item = self.capability_proposal_repository.get_by_id(proposal_id=proposal_id)
        if item is None:
            raise ValueError("Capability proposal not found")

        if item.status != "validated":
            raise ValueError("Only validated proposal can be rejected")

        try:
            self.capability_proposal_repository.update_status(
                item=item,
                status="rejected",
            )
            self.capability_proposal_repository.commit()

            return {
                "success": True,
                "proposal_id": item.id,
                "capability_name": item.capability_name,
                "proposal_type": item.proposal_type,
                "status": item.status,
            }
        except Exception:
            self.capability_proposal_repository.rollback()
            raise