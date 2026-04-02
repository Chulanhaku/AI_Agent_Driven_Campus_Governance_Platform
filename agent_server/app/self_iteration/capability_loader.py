from app.self_iteration.capability_registry import CapabilityRegistry


class CapabilityLoader:
    def __init__(self, capability_registry: CapabilityRegistry) -> None:
        self.capability_registry = capability_registry

    def load(
        self,
        *,
        proposal: dict,
    ) -> dict:
        proposal_type = proposal.get("proposal_type")

        if proposal_type == "knowledge_patch":
            target_intent = proposal.get("target_intent")
            aliases = proposal.get("intent_aliases", [])

            for alias in aliases:
                self.capability_registry.register_intent_alias(
                    alias=alias,
                    target_intent=target_intent,
                )

            return {
                "activated": True,
                "activation_type": "knowledge_patch",
                "loaded_count": len(aliases),
            }

        if proposal_type == "plan_patch":
            capability_name = proposal.get("capability_name") or "unnamed_plan_patch"
            planner_patch = proposal.get("planner_patch", {})

            self.capability_registry.register_plan_patch(
                capability_name=capability_name,
                plan_patch=planner_patch,
            )

            return {
                "activated": True,
                "activation_type": "plan_patch",
                "loaded_count": 1,
            }

        return {
            "activated": False,
            "activation_type": proposal_type,
            "loaded_count": 0,
        }