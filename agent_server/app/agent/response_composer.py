from app.llm.base import BaseLlmProvider


class ResponseComposer:
    def __init__(self, llm_provider: BaseLlmProvider) -> None:
        self.llm_provider = llm_provider

    def compose(
        self,
        *,
        user_name: str,
        user_message: str,
        primary_intent: str,
        secondary_intents: list[str],
        tool_result_summary: str,
        reasoning_result_summary: str | None,
        memory_summary: str | None,
    ) -> str:
        combined_summary = tool_result_summary
        if reasoning_result_summary:
            combined_summary = f"{tool_result_summary}\n\n补充分析：\n{reasoning_result_summary}"

        try:
            return self.llm_provider.compose_tool_response(
                user_name=user_name,
                user_message=user_message,
                primary_intent=primary_intent,
                secondary_intents=secondary_intents,
                tool_result_summary=combined_summary,
                memory_summary=memory_summary,
            )
        except Exception:
            return combined_summary