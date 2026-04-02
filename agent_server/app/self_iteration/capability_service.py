from app.self_iteration.capability_designer import CapabilityDesigner
from app.self_iteration.capability_detector import CapabilityDetector
from app.self_iteration.capability_researcher import CapabilityResearcher
from app.self_iteration.capability_validator import CapabilityValidator
from app.self_iteration.capability_loader import CapabilityLoader
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
    ) -> None:
        self.capability_proposal_repository = capability_proposal_repository
        self.capability_detector = capability_detector
        self.capability_researcher = capability_researcher
        self.capability_designer = capability_designer
        self.capability_validator = capability_validator
        self.capability_loader = capability_loader

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
            item = self.capability_proposal_repository.create_proposal(
                session_id=session_id,
                user_id=user_id,
                trigger_message=user_message,
                proposal_type=proposal_type,
                capability_name=capability_name,
                research_summary_json=research_summary,
                proposal_json=proposal,
                status="draft",
            )

            validation_result = self.capability_validator.validate(proposal=proposal)

            activation_result = None
            final_status = "draft"

            if validation_result["valid"]:
                if proposal_type in {"knowledge_patch", "plan_patch"}:
                    activation_result = self.capability_loader.load(proposal=proposal)
                    final_status = "activated" if activation_result.get("activated") else "validated"
                else:
                    final_status = "validated"
            else:
                final_status = "rejected"

            self.capability_proposal_repository.update_status(
                item=item,
                status=final_status,
            )
            self.capability_proposal_repository.commit()

            return {
                "success": True,
                "proposal_id": item.id,
                "proposal_type": item.proposal_type,
                "capability_name": item.capability_name,
                "proposal": proposal,
                "validation_result": validation_result,
                "activation_result": activation_result,
                "status": final_status,
            }
        except Exception:
            self.capability_proposal_repository.rollback()
            raise
