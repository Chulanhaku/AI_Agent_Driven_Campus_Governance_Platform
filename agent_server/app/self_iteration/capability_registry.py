class CapabilityRegistry:
    def __init__(self) -> None:
        self.intent_aliases: dict[str, str] = {}
        self.plan_patches: dict[str, dict] = {}

    def clear(self) -> None:
        self.intent_aliases.clear()
        self.plan_patches.clear()

    def register_intent_alias(
        self,
        *,
        alias: str,
        target_intent: str,
    ) -> None:
        self.intent_aliases[alias.strip().lower()] = target_intent

    def register_plan_patch(
        self,
        *,
        capability_name: str,
        plan_patch: dict,
    ) -> None:
        self.plan_patches[capability_name] = plan_patch

    def resolve_intent_alias(
        self,
        *,
        message: str,
    ) -> str | None:
        normalized = message.strip().lower()
        for alias, target_intent in self.intent_aliases.items():
            if alias in normalized:
                return target_intent
        return None

    def get_plan_patch_for_intent(
        self,
        *,
        primary_intent: str,
    ) -> dict | None:
        for _, patch in self.plan_patches.items():
            if patch.get("primary_intent") == primary_intent:
                return patch
        return None

    def snapshot(self) -> dict:
        return {
            "intent_aliases": dict(self.intent_aliases),
            "plan_patches": dict(self.plan_patches),
            "intent_alias_count": len(self.intent_aliases),
            "plan_patch_count": len(self.plan_patches),
        }