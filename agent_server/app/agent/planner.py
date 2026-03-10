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

        return {
            "action": "fallback",
        }