from abc import ABC, abstractmethod


class BaseLlmProvider(ABC):
    @abstractmethod
    def classify_intent(
        self,
        *,
        message: str,
        recent_messages_text: str | None = None,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    def extract_slots(self, *, intent: str, message: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def generate_fallback_reply(self, *, user_name: str, message: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def answer_with_context(
        self,
        *,
        user_name: str,
        question: str,
        context_text: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_session_title(self, *, messages_text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def summarize_session(
        self,
        *,
        existing_summary: str,
        recent_messages_text: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def compose_tool_response(
        self,
        *,
        user_name: str,
        user_message: str,
        primary_intent: str,
        secondary_intents: list[str],
        tool_result_summary: str,
        memory_summary: str | None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_execution_plan(
        self,
        *,
        user_message: str,
        available_tools: list[str],
        primary_intent: str,
        secondary_intents: list[str],
        memory_summary: str | None,
    ) -> dict:
        raise NotImplementedError