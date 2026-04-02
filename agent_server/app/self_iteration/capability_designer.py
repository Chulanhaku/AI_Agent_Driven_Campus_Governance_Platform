from app.llm.base import BaseLlmProvider


class CapabilityDesigner:
    def __init__(self, llm_provider: BaseLlmProvider) -> None:
        self.llm_provider = llm_provider

    def design(
        self,
        *,
        user_message: str,
        research_summary: dict,
        memory_summary: str | None,
    ) -> dict:
        if hasattr(self.llm_provider, "generate_capability_proposal"):
            return self.llm_provider.generate_capability_proposal(
                user_message=user_message,
                research_summary=research_summary,
                memory_summary=memory_summary,
            )

        return {
            "proposal_type": "tool_spec",
            "capability_name": "unknown_capability",
            "needs_new_tool": True,
            "reason": "当前 provider 未实现 generate_capability_proposal",
        }