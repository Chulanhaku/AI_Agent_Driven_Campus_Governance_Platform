class DynamicToolRegistry:
    def __init__(self) -> None:
        self._tools_by_name: dict[str, dict] = {}
        self._tools_by_intent: dict[str, list[dict]] = {}

    def clear(self) -> None:
        self._tools_by_name.clear()
        self._tools_by_intent.clear()

    def register_tool(
        self,
        *,
        tool_definition: dict,
    ) -> None:
        tool_name = tool_definition["tool_name"]
        primary_intent = tool_definition.get("primary_intent")

        self._tools_by_name[tool_name] = tool_definition

        if primary_intent:
            self._tools_by_intent.setdefault(primary_intent, [])
            self._tools_by_intent[primary_intent].append(tool_definition)

    def get_tool(
        self,
        *,
        tool_name: str,
    ) -> dict | None:
        return self._tools_by_name.get(tool_name)

    def list_tools_by_intent(
        self,
        *,
        primary_intent: str,
    ) -> list[dict]:
        return list(self._tools_by_intent.get(primary_intent, []))

    def snapshot(self) -> dict:
        return {
            "tool_count": len(self._tools_by_name),
            "tools": dict(self._tools_by_name),
            "tools_by_intent": {
                key: [item["tool_name"] for item in value]
                for key, value in self._tools_by_intent.items()
            },
        }