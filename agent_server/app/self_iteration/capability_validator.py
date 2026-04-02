from app.agent.plan_schema import ExecutionPlanSchema


class CapabilityValidator:
    def __init__(self) -> None:
        self.allowed_proposal_types = {
            "knowledge_patch",
            "plan_patch",
            "tool_spec",
        }
        self.allowed_intents = {
            "query_schedule",
            "campus_card_topup",
            "leave_create",
            "policy_qa",
            "course_plan_generate",
            "course_plan_submit",
            "resource_booking_generate",
            "resource_booking_submit",
            "zero_form_approval_generate",
            "zero_form_approval_submit",
            "fallback",
        }
        self.allowed_goals = {
            "time_planning_advice",
            "weekly_busyness_analysis",
        }
        self.allowed_tool_names = {
            "query_my_schedule",
            "query_policy_knowledge",
            "generate_course_plan",
            "query_available_resources",
            "generate_zero_form_approval",
        }

    def validate(
        self,
        *,
        proposal: dict,
    ) -> dict:
        proposal_type = proposal.get("proposal_type")
        if proposal_type not in self.allowed_proposal_types:
            return {
                "valid": False,
                "reason": f"proposal_type not allowed: {proposal_type}",
            }

        if proposal_type == "knowledge_patch":
            return self._validate_knowledge_patch(proposal=proposal)

        if proposal_type == "plan_patch":
            return self._validate_plan_patch(proposal=proposal)

        return {
            "valid": True,
            "reason": "tool_spec kept as non-auto-activatable draft",
        }

    def _validate_knowledge_patch(
        self,
        *,
        proposal: dict,
    ) -> dict:
        target_intent = proposal.get("target_intent")
        aliases = proposal.get("intent_aliases", [])

        if target_intent not in self.allowed_intents:
            return {
                "valid": False,
                "reason": f"target_intent not allowed: {target_intent}",
            }

        if not isinstance(aliases, list) or not aliases:
            return {
                "valid": False,
                "reason": "intent_aliases must be a non-empty list",
            }

        return {
            "valid": True,
            "reason": "knowledge_patch validated",
        }

    def _validate_plan_patch(
        self,
        *,
        proposal: dict,
    ) -> dict:
        planner_patch = proposal.get("planner_patch")
        if not isinstance(planner_patch, dict):
            return {
                "valid": False,
                "reason": "planner_patch missing",
            }

        primary_intent = planner_patch.get("primary_intent")
        if primary_intent not in self.allowed_intents:
            return {
                "valid": False,
                "reason": f"planner primary_intent not allowed: {primary_intent}",
            }

        steps = planner_patch.get("steps", [])
        try:
            ExecutionPlanSchema(
                plan_type="multi_step",
                steps=steps,
            )
        except Exception as exc:
            return {
                "valid": False,
                "reason": f"planner_patch schema invalid: {exc}",
            }

        for step in steps:
            step_type = step.get("type")
            if step_type == "call_tool":
                tool_name = step.get("tool_name")
                if tool_name not in self.allowed_tool_names:
                    return {
                        "valid": False,
                        "reason": f"tool_name not allowed: {tool_name}",
                    }
            if step_type == "reason":
                goal = step.get("goal")
                if goal not in self.allowed_goals:
                    return {
                        "valid": False,
                        "reason": f"reasoning goal not allowed: {goal}",
                    }

        return {
            "valid": True,
            "reason": "plan_patch validated",
        }
