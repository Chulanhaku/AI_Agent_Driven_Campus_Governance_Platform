from app.agent.reasoning import ReasoningEngine
from app.tools.registry import ToolRegistry


class Executor:
    def __init__(self) -> None:
        self.reasoning_engine = ReasoningEngine()

    def execute_plan(
        self,
        *,
        plan: dict,
        tool_registry: ToolRegistry,
        user_message: str,
    ) -> dict:
        steps = plan.get("steps", [])
        tool_results: dict = {}
        reasoning_results: dict = {}

        for step in steps:
            step_type = step.get("type")

            if step_type == "call_tool":
                tool_name = step["tool_name"]
                params = step.get("params", {})

                tool = tool_registry.get(tool_name)
                if tool is None:
                    return {
                        "success": False,
                        "error": f"Tool not found: {tool_name}",
                        "tool_results": tool_results,
                        "reasoning_results": reasoning_results,
                    }

                result = tool.run(**params)
                tool_results[tool_name] = result

                if not result.get("success"):
                    return {
                        "success": False,
                        "error": f"Tool execution failed: {tool_name}",
                        "tool_results": tool_results,
                        "reasoning_results": reasoning_results,
                    }

            elif step_type == "reason":
                goal = step["goal"]

                result = self.reasoning_engine.reason(
                    goal=goal,
                    tool_results=tool_results,
                    user_message=user_message,
                )
                reasoning_results[goal] = result

            elif step_type == "compose":
                continue

            elif step_type == "fallback":
                return {
                    "success": False,
                    "fallback": True,
                    "tool_results": tool_results,
                    "reasoning_results": reasoning_results,
                }

            elif step_type in {"create_pending_topup", "create_pending_leave"}:
                return {
                    "success": True,
                    "workflow_step": step,
                    "tool_results": tool_results,
                    "reasoning_results": reasoning_results,
                }

        return {
            "success": True,
            "tool_results": tool_results,
            "reasoning_results": reasoning_results,
        }