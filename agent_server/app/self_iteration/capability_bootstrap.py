from app.db.repositories.capability_proposal_repository import CapabilityProposalRepository
from app.self_iteration.capability_loader import CapabilityLoader


class CapabilityBootstrap:
    def __init__(
        self,
        capability_proposal_repository: CapabilityProposalRepository,
        capability_loader: CapabilityLoader,
    ) -> None:
        self.capability_proposal_repository = capability_proposal_repository
        self.capability_loader = capability_loader

    def reload_activated_proposals(self) -> dict:
        items = self.capability_proposal_repository.list_activated(limit=500)

        proposals = [item.proposal_json for item in items]
        load_result = self.capability_loader.load_many(
            proposals=proposals,
            reset_first=True,
        )

        return {
            "success": True,
            "activated_proposal_count": len(items),
            "registry_load_result": load_result,
        }