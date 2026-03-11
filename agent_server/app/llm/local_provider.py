from app.llm.base import BaseLlmProvider


class LocalLlmProvider(BaseLlmProvider):
    def classify_intent(self, *, message: str) -> dict:
        return {
            "intent": "fallback",
            "confidence": 0.0,
        }

    def extract_slots(self, *, intent: str, message: str) -> dict:
        return {}

    def generate_fallback_reply(self, *, user_name: str, message: str) -> str:
        return (
            f"你好，{user_name}。我已经收到你的消息：{message}。"
            "当前模型提供器还处于 mock/local 占位状态，所以这里只返回一条基础回复。"
        )

    def answer_with_context(
        self,
        *,
        user_name: str,
        question: str,
        context_text: str,
    ) -> str:
        return (
            f"我检索到了以下制度内容，可供参考：\n\n"
            f"{context_text}\n\n"
            f"你的问题是：{question}\n"
            f"当前是本地/mock 模式，所以先直接返回检索结果摘要。"
        )