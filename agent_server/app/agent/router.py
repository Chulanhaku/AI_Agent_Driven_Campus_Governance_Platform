import re

from app.llm.base import BaseLlmProvider


class AgentRouter:
    def __init__(self, llm_provider: BaseLlmProvider | None = None) -> None:
        self.llm_provider = llm_provider

    def detect_intent(self, message: str) -> str:
        rule_intent = self._detect_intent_by_rules(message)
        if rule_intent != "fallback":
            return rule_intent

        if self.llm_provider is not None:
            try:
                result = self.llm_provider.classify_intent(message=message)
                intent = result.get("intent", "fallback")
                if intent in {
                    "query_schedule",
                    "campus_card_topup",
                    "leave_create",
                    "fallback",
                }:
                    return intent
            except Exception:
                pass

        return "fallback"

    def _detect_intent_by_rules(self, message: str) -> str:
        normalized = message.strip().lower()

        leave_keywords = [
            "请假",
            "我要请假",
            "请病假",
            "请事假",
            "leave",
        ]
        for keyword in leave_keywords:
            if keyword in normalized:
                return "leave_create"

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

    def extract_leave_days(self, message: str) -> int | None:
        match = re.search(r"(\d+)\s*天", message)
        if match:
            return int(match.group(1))
        return None

    def extract_leave_reason(self, message: str) -> str | None:
        patterns = [
            r"原因是(.+)$",
            r"因为(.+)$",
            r"原因[:：]\s*(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                reason = match.group(1).strip()
                if reason:
                    return reason

        return None

    def extract_slots_with_llm(self, *, intent: str, message: str) -> dict:
        if self.llm_provider is None:
            return {}

        try:
            return self.llm_provider.extract_slots(intent=intent, message=message)
        except Exception:
            return {}