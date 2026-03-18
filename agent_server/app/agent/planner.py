from app.agent.plan_schema import ExecutionPlanSchema
from app.llm.base import BaseLlmProvider


class Planner:
    def __init__(self, llm_provider: BaseLlmProvider | None = None) -> None:
        self.llm_provider = llm_provider

    def build_plan(
        self,
        *,
        intent: str,
        context: dict,
        use_llm_planner: bool = False,
    ) -> dict:
        if use_llm_planner and self.llm_provider is not None:
            llm_plan = self._build_plan_by_llm(intent=intent, context=context)
            if llm_plan is not None:
                return llm_plan

        return self._build_plan_by_rules(intent=intent, context=context)

    def _build_plan_by_llm(
        self,
        *,
        intent: str,
        context: dict,
    ) -> dict | None:
        try:
            raw_plan = self.llm_provider.generate_execution_plan(
                user_message=context["message"],
                available_tools=context.get("available_tools", []),
                primary_intent=intent,
                secondary_intents=context.get("secondary_intents", []),
                memory_summary=context.get("memory", {}).get("summary_text"),
            )

            plan = self._validate_and_normalize_plan(raw_plan, context=context)
            return plan
        except Exception:
            return None

    def _build_plan_by_rules(
        self,
        *,
        intent: str,
        context: dict,
    ) -> dict:
        secondary_intents = context.get("secondary_intents", [])
        print(intent, secondary_intents)
        if intent == "query_schedule":
            steps = [
                {
                    "type": "call_tool",
                    "tool_name": "query_my_schedule",
                    "params": {
                        "user_id": context["current_user"]["id"],
                        "semester": None,
                        "weekday": None,
                    },
                }
            ]

            if "time_planning_advice" in secondary_intents:
                steps.append(
                    {
                        "type": "reason",
                        "goal": "time_planning_advice",
                    }
                )

            if "weekly_busyness_analysis" in secondary_intents:
                steps.append(
                    {
                        "type": "reason",
                        "goal": "weekly_busyness_analysis",
                    }
                )

            steps.append({"type": "compose"})

            return {
                "plan_type": "multi_step",
                "steps": steps,
            }

        if intent == "campus_card_topup":
            return {
                "plan_type": "workflow",
                "steps": [
                    {
                        "type": "create_pending_topup",
                        "params": {
                            "user_id": context["current_user"]["id"],
                            "session_id": context["session_id"],
                            "amount": context.get("amount"),
                        },
                    }
                ],
            }

        if intent == "leave_create":
            return {
                "plan_type": "workflow",
                "steps": [
                    {
                        "type": "create_pending_leave",
                        "params": {
                            "user_id": context["current_user"]["id"],
                            "session_id": context["session_id"],
                            "days": context.get("leave_days"),
                            "reason": context.get("leave_reason"),
                            "leave_type": "sick",
                        },
                    }
                ],
            }

        if intent == "policy_qa":
            return {
                "plan_type": "multi_step",
                "steps": [
                    {
                        "type": "call_tool",
                        "tool_name": "query_policy_knowledge",
                        "params": {
                            "question": context["message"],
                        },
                    },
                    {
                        "type": "compose",
                    },
                ],
            }

        if intent == "course_plan_generate":
            return {
                "plan_type": "multi_step",
                "steps": [
                    {
                        "type": "call_tool",
                        "tool_name": "generate_course_plan",
                        "params": {
                            "user_id": context["current_user"]["id"],
                            "semester": context.get("semester") or "2026-spring",
                            "max_plan_count": 3,
                        },
                    },
                    {
                        "type": "compose",
                    },
                ],
            }
        
        if intent == "course_plan_submit":
            return {
                "plan_type": "workflow",
                "steps": [
                    {
                        "type": "create_pending_course_plan_submit",
                        "params": {
                            "user_id": context["current_user"]["id"],
                            "session_id": context["session_id"],
                            "selected_plan_index": context.get("selected_plan_index"),
                        },
                    }
                ],
            }

        return {
            "plan_type": "fallback",
            "steps": [
                {
                    "type": "fallback",
                }
            ],
        }
    

    def _validate_and_normalize_plan(
        self,
        raw_plan: dict,
        *,
        context: dict,
    ) -> dict:
        schema_obj = ExecutionPlanSchema(**raw_plan)
        plan = schema_obj.model_dump()

        allowed_tools = set(context.get("available_tools", []))
        allowed_goals = {
            "time_planning_advice",
            "weekly_busyness_analysis",
        }

        for step in plan["steps"]:
            step_type = step["type"]

            if step_type == "call_tool":
                tool_name = step.get("tool_name")
                if tool_name not in allowed_tools:
                    raise ValueError(f"Tool not allowed: {tool_name}")

                params = step.get("params") or {}
                if params.get("user_id") == "$CURRENT_USER_ID":
                    params["user_id"] = context["current_user"]["id"]
                step["params"] = params

                if tool_name in {"generate_course_plan", "query_my_schedule"}:
                    semester = (
                        params.get("semester")
                        or context.get("semester")
                        or "2026-spring"
                    )
                    params["semester"] = self._normalize_semester(semester)
                if tool_name == "generate_course_plan":
                    if "max_plan_count" not in params:
                        params["max_plan_count"] = 3

            elif step_type == "reason":
                goal = step.get("goal")
                if goal not in allowed_goals:
                    raise ValueError(f"Reasoning goal not allowed: {goal}")

        return plan
    
    def _normalize_semester(self, value: str | None) -> str | None:
        if not value:
            return None
        return value.strip().lower().replace("_", "-")