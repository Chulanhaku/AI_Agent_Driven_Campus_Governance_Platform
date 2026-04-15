from app.db.repositories.capability_proposal_repository import CapabilityProposalRepository
from app.db.repositories.dynamic_plan_definition_repository import DynamicPlanDefinitionRepository
from app.db.repositories.dynamic_tool_definition_repository import DynamicToolDefinitionRepository
from app.self_iteration.dynamic_definition_factory import DynamicDefinitionFactory
from app.self_iteration.dynamic_capability_bootstrap import DynamicCapabilityBootstrap


class DynamicDefinitionService:
    def __init__(
        self,
        capability_proposal_repository: CapabilityProposalRepository,
        dynamic_tool_definition_repository: DynamicToolDefinitionRepository,
        dynamic_plan_definition_repository: DynamicPlanDefinitionRepository,
        dynamic_definition_factory: DynamicDefinitionFactory,
        dynamic_capability_bootstrap: DynamicCapabilityBootstrap,
    ) -> None:
        self.capability_proposal_repository = capability_proposal_repository
        self.dynamic_tool_definition_repository = dynamic_tool_definition_repository
        self.dynamic_plan_definition_repository = dynamic_plan_definition_repository
        self.dynamic_definition_factory = dynamic_definition_factory
        self.dynamic_capability_bootstrap = dynamic_capability_bootstrap

    def register_from_tool_spec_proposal(
        self,
        *,
        proposal_id: int,
    ) -> dict:
        proposal_item = self.capability_proposal_repository.get_by_id(
            proposal_id=proposal_id,
        )
        if proposal_item is None:
            raise ValueError("Capability proposal not found")

        if proposal_item.proposal_type != "tool_spec":
            raise ValueError("Only tool_spec proposal can be registered as dynamic capability")

        if proposal_item.status not in {"validated", "activated"}:
            raise ValueError("Only validated/activated tool_spec proposal can be registered")

        generated = self.dynamic_definition_factory.build_from_tool_spec_proposal(
            proposal_id=proposal_item.id,
            proposal=proposal_item.proposal_json,
        )

        tool_def = generated["dynamic_tool_definition"]
        plan_def = generated["dynamic_plan_definition"]

        try:
            existed_tool = self.dynamic_tool_definition_repository.get_by_tool_name(
                tool_name=tool_def["tool_name"],
            )
            if existed_tool is None:
                self.dynamic_tool_definition_repository.create_definition(**tool_def)

            existed_plan = self.dynamic_plan_definition_repository.get_by_primary_intent(
                primary_intent=plan_def["primary_intent"],
            )
            if existed_plan is None:
                self.dynamic_plan_definition_repository.create_definition(**plan_def)

            self.dynamic_tool_definition_repository.commit()
            self.dynamic_plan_definition_repository.commit()

            reload_result = self.dynamic_capability_bootstrap.reload_active_definitions()

            return {
                "success": True,
                "proposal_id": proposal_item.id,
                "tool_name": tool_def["tool_name"],
                "primary_intent": plan_def["primary_intent"],
                "reload_result": reload_result,
            }
        except Exception:
            self.dynamic_tool_definition_repository.rollback()
            self.dynamic_plan_definition_repository.rollback()
            raise