class CapabilityDetector:
    def should_propose(
        self,
        *,
        user_message: str,
    ) -> bool:
        normalized = user_message.strip().lower()

        strong_keywords = [
            "帮我查",
            "帮我预约",
            "帮我申请",
            "帮我生成",
            "帮我导出",
            "帮我安排",
            "怎么查",
            "怎么申请",
            "怎么预约",
            "怎么导出",
            "想缴",
            "想查",
            "想申请",
        ]
        if any(keyword in normalized for keyword in strong_keywords):
            return True

        return False