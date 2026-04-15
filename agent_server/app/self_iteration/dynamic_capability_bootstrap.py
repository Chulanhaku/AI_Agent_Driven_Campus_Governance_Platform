from app.db.repositories.dynamic_plan_definition_repository import DynamicPlanDefinitionRepository
from app.db.repositories.dynamic_tool_definition_repository import DynamicToolDefinitionRepository
from app.self_iteration.dynamic_plan_registry import DynamicPlanRegistry
from app.self_iteration.dynamic_tool_registry import DynamicToolRegistry


class DynamicCapabilityBootstrap:
    def __init__(
        self,
        dynamic_tool_definition_repository: DynamicToolDefinitionRepository,
        dynamic_plan_definition_repository: DynamicPlanDefinitionRepository,
        dynamic_tool_registry: DynamicToolRegistry,
        dynamic_plan_registry: DynamicPlanRegistry,
    ) -> None:
        self.dynamic_tool_definition_repository = dynamic_tool_definition_repository
        self.dynamic_plan_definition_repository = dynamic_plan_definition_repository
        self.dynamic_tool_registry = dynamic_tool_registry
        self.dynamic_plan_registry = dynamic_plan_registry

    def reload_active_definitions(self) -> dict:
        self.dynamic_tool_registry.clear()
        self.dynamic_plan_registry.clear()

        tool_items = self.dynamic_tool_definition_repository.list_active(limit=500)
        plan_items = self.dynamic_plan_definition_repository.list_active(limit=500)

        for item in tool_items:
            self.dynamic_tool_registry.register_tool(
                tool_definition={
                    "id": item.id,
                    "source_proposal_id": item.source_proposal_id,
                    "tool_name": item.tool_name,
                    "primary_intent": item.primary_intent,
                    "tool_type": item.tool_type,
                    "description": item.description,
                    "input_schema_json": item.input_schema_json,
                    "execution_config_json": item.execution_config_json,
                    "status": item.status,
                }
            )

        for item in plan_items:
            self.dynamic_plan_registry.register_plan(
                primary_intent=item.primary_intent,
                plan_definition=item.plan_json,
            )

        return {
            "success": True,
            "dynamic_tool_count": len(tool_items),
            "dynamic_plan_count": len(plan_items),
        }