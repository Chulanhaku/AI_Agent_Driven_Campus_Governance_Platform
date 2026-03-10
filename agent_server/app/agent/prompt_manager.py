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