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
        memory_summary: str | None,
    ) -> str:
        try:
            return self.llm_provider.compose_tool_response(
                user_name=user_name,
                user_message=user_message,
                primary_intent=primary_intent,
                secondary_intents=secondary_intents,
                tool_result_summary=tool_result_summary,
                memory_summary=memory_summary,
            )
        except Exception:
            return tool_result_summary