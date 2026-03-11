from abc import ABC, abstractmethod


class BaseLlmProvider(ABC):
    @abstractmethod
    def classify_intent(self, *, message: str) -> dict:
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