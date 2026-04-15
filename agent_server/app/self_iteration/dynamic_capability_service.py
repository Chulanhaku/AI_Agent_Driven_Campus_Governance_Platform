from app.self_iteration.dynamic_plan_registry import DynamicPlanRegistry
from app.self_iteration.dynamic_tool_registry import DynamicToolRegistry
from app.self_iteration.dynamic_tool_executor import DynamicToolExecutor


class DynamicCapabilityService:
    def __init__(
        self,
        dynamic_plan_registry: DynamicPlanRegistry,
        dynamic_tool_registry: DynamicToolRegistry,
        dynamic_tool_executor: DynamicToolExecutor,
        response_composer,
    ) -> None:
        self.dynamic_plan_registry = dynamic_plan_registry
        self.dynamic_tool_registry = dynamic_tool_registry
        self.dynamic_tool_executor = dynamic_tool_executor
        self.response_composer = response_composer

    def try_execute(
        self,
        *,
        current_user,
        user_message: str,
        primary_intent: str,
        secondary_intents: list[str],
        parsed_slots: dict,
        memory_context: dict,
    ) -> dict | None:
        dynamic_plan = self.dynamic_plan_registry.get_plan(
            primary_intent=primary_intent,
        )
        if dynamic_plan is None:
            return None

        steps = dynamic_plan.get("steps", [])
        tool_results: list[dict] = []

        for step in steps:
            step_type = step.get("type")

            if step_type == "call_dynamic_tool":
                tool_name = step.get("tool_name")
                tool_definition = self.dynamic_tool_registry.get_tool(tool_name=tool_name)
                if tool_definition is None:
                    return {
                        "success": False,
                        "dynamic_matched": True,
                        "message": f"dynamic tool not found: {tool_name}",
                    }

                params_template = step.get("params_template", {}) or {}
                bound_params = self._bind_params(
                    params_template=params_template,
                    parsed_slots=parsed_slots,
                    current_user=current_user,
                    memory_context=memory_context,
                )

                result = self.dynamic_tool_executor.execute_tool(
                    tool_definition=tool_definition,
                    params=bound_params,
                )
                if not result.get("success"):
                    return {
                        "success": False,
                        "dynamic_matched": True,
                        "message": result.get("message", "dynamic tool execution failed"),
                    }

                tool_results.append(result)

            elif step_type == "compose_dynamic":
                continue

        tool_result_summary = self._build_tool_result_summary(
            primary_intent=primary_intent,
            tool_results=tool_results,
        )

        reply = self.response_composer.compose(
            user_name=current_user.full_name,
            user_message=user_message,
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            tool_result_summary=tool_result_summary,
            reasoning_result_summary=None,
            memory_summary=memory_context.get("summary_text"),
        )

        return {
            "success": True,
            "dynamic_matched": True,
            "reply": reply,
            "tool_results": tool_results,
            "tool_result_summary": tool_result_summary,
        }

    def _bind_params(
        self,
        *,
        params_template: dict,
        parsed_slots: dict,
        current_user,
        memory_context: dict,
    ) -> dict:
        bound = {}

        for key, value in params_template.items():
            if isinstance(value, str) and value.startswith("$slot."):
                slot_name = value.replace("$slot.", "", 1)
                bound[key] = parsed_slots.get(slot_name)
            elif isinstance(value, str) and value.startswith("$context."):
                context_name = value.replace("$context.", "", 1)
                if context_name == "current_user_id":
                    bound[key] = current_user.id
                else:
                    bound[key] = None
            elif isinstance(value, str) and value.startswith("$memory."):
                memory_name = value.replace("$memory.", "", 1)
                bound[key] = memory_context.get(memory_name)
            else:
                bound[key] = value

        return bound

    def _build_tool_result_summary(
        self,
        *,
        primary_intent: str,
        tool_results: list[dict],
    ) -> str:
        if not tool_results:
            return "未查询到动态工具结果。"

        lines = [f"已通过动态能力完成 {primary_intent} 查询。"]
        for result in tool_results:
            lines.append(
                f"动态工具 {result.get('tool_name')} 返回 {result.get('row_count', 0)} 条结果。"
            )

            if result.get("tool_type") == "db_query":
                rows = result.get("rows", [])
                for row in rows[:5]:
                    lines.append(str(row))

            elif result.get("tool_type") == "web_search":
                results = result.get("results", [])
                for item in results[:5]:
                    lines.append(str(item))

        return "\n".join(lines)