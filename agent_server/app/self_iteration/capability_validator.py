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
        llm_confidence = float(proposal.get("confidence_score", 0.5) or 0.5)
        llm_risk = proposal.get("risk_level", "medium") or "medium"

        if proposal_type not in self.allowed_proposal_types:
            return {
                "valid": False,
                "reason": f"proposal_type not allowed: {proposal_type}",
                "confidence_score": 0.0,
                "risk_level": "high",
                "activation_policy_candidate": "reject",
            }

        if proposal_type == "knowledge_patch":
            result = self._validate_knowledge_patch(proposal=proposal)
        elif proposal_type == "plan_patch":
            result = self._validate_plan_patch(proposal=proposal)
        else:
            result = {
                "valid": True,
                "reason": "tool_spec kept as non-auto-activatable draft",
            }

        # 轻量合成置信度和风险
        confidence_score = llm_confidence
        risk_level = llm_risk

        if not result["valid"]:
            confidence_score = min(confidence_score, 0.2)
            risk_level = "high"

        if proposal_type == "tool_spec":
            risk_level = "high"

        if proposal_type == "knowledge_patch" and result["valid"]:
            risk_level = "low" if llm_risk in {"low", "medium"} else llm_risk

        if proposal_type == "plan_patch" and result["valid"]:
            if risk_level == "low":
                risk_level = "medium"

        activation_policy_candidate = "review_required"
        if not result["valid"]:
            activation_policy_candidate = "reject"
        elif proposal_type == "knowledge_patch" and confidence_score >= 0.75 and risk_level == "low":
            activation_policy_candidate = "auto_activate"
        elif proposal_type == "plan_patch" and confidence_score >= 0.88 and risk_level == "medium":
            activation_policy_candidate = "auto_activate"
        else:
            activation_policy_candidate = "review_required"

        return {
            "valid": result["valid"],
            "reason": result["reason"],
            "confidence_score": round(confidence_score, 4),
            "risk_level": risk_level,
            "activation_policy_candidate": activation_policy_candidate,
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