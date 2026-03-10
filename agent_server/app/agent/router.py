import re


class AgentRouter:
    def detect_intent(self, message: str) -> str:
        normalized = message.strip().lower()

        topup_keywords = [
            "充值",
            "充钱",
            "充校园卡",
            "校园卡充值",
            "topup",
            "recharge",
        ]
        for keyword in topup_keywords:
            if keyword in normalized:
                return "campus_card_topup"

        schedule_keywords = [
            "课表",
            "课程表",
            "schedule",
            "明天上什么课",
            "今天上什么课",
            "这周课表",
            "今天课表",
            "明天课表",
        ]
        for keyword in schedule_keywords:
            if keyword in normalized:
                return "query_schedule"

        return "fallback"

    def extract_amount(self, message: str) -> str | None:
        match = re.search(r"(\d+(?:\.\d{1,2})?)", message)
        if match:
            return match.group(1)
        return None