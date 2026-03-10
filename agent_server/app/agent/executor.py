from app.tools.registry import ToolRegistry


class Executor:
    def execute(
        self,
        *,
        plan: dict,
        tool_registry: ToolRegistry,
    ) -> dict:
        action = plan.get("action")

        if action == "call_tool":
            tool_name = plan["tool_name"]
            params = plan.get("params", {})

            tool = tool_registry.get(tool_name)
            if tool is None:
                return {
                    "success": False,
                    "error": f"Tool not found: {tool_name}",
                    "action": "fallback",
                }

            return tool.run(**params)

        return {
            "success": False,
            "action": "fallback",
        }