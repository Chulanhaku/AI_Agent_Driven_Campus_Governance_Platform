class Planner:
    def build_plan(self, *, intent: str, context: dict) -> dict:
        if intent == "query_schedule":
            return {
                "action": "call_tool",
                "tool_name": "query_my_schedule",
                "params": {
                    "user_id": context["current_user"]["id"],
                    "semester": None,
                    "weekday": None,
                },
            }

        if intent == "campus_card_topup":
            return {
                "action": "create_pending_topup",
                "params": {
                    "user_id": context["current_user"]["id"],
                    "session_id": context["session_id"],
                    "amount": context.get("amount"),
                },
            }

        if intent == "leave_create":
            return {
                "action": "create_pending_leave",
                "params": {
                    "user_id": context["current_user"]["id"],
                    "session_id": context["session_id"],
                    "days": context.get("leave_days"),
                    "reason": context.get("leave_reason"),
                    "leave_type": "sick",
                },
            }

        if intent == "policy_qa":
            return {
                "action": "call_tool",
                "tool_name": "query_policy_knowledge",
                "params": {
                    "question": context["message"],
                },
            }

        return {
            "action": "fallback",
        }