class PromptManager:
    def build_fallback_prompt(
        self,
        *,
        user_name: str,
        message: str,
    ) -> dict:
        return {
            "user_name": user_name,
            "message": message,
        }

    def should_use_llm_planner(
        self,
        *,
        primary_intent: str,
        secondary_intents: list[str],
        user_message: str,
    ) -> bool:
        if primary_intent in {"campus_card_topup", "leave_create"}:
            return False

        if len(secondary_intents) >= 1:
            return True

        complex_keywords = [
            "然后",
            "顺便",
            "并且",
            "再帮我",
            "另外",
            "同时",
        ]
        normalized = user_message.strip().lower()

        if any(keyword in normalized for keyword in complex_keywords):
            return True

        return False