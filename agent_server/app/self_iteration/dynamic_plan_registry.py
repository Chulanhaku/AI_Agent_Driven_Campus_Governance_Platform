class DynamicPlanRegistry:
    def __init__(self) -> None:
        self._plans_by_intent: dict[str, dict] = {}

    def clear(self) -> None:
        self._plans_by_intent.clear()

    def register_plan(
        self,
        *,
        primary_intent: str,
        plan_definition: dict,
    ) -> None:
        self._plans_by_intent[primary_intent] = plan_definition

    def get_plan(
        self,
        *,
        primary_intent: str,
    ) -> dict | None:
        return self._plans_by_intent.get(primary_intent)

    def list_primary_intents(self) -> list[str]:
        return list(self._plans_by_intent.keys())

    def snapshot(self) -> dict:
        return {
            "plan_count": len(self._plans_by_intent),
            "primary_intents": list(self._plans_by_intent.keys()),
            "plans": dict(self._plans_by_intent),
        }