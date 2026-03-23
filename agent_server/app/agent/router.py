import re

from app.llm.base import BaseLlmProvider
from datetime import datetime, timedelta

class AgentRouter:
    def __init__(self, llm_provider: BaseLlmProvider | None = None) -> None:
        self.llm_provider = llm_provider

    # def detect_intent(self, message: str) -> str:
    #     rule_intent = self._detect_intent_by_rules(message)
    #     if rule_intent != "fallback":
    #         return rule_intent

    #     if self.llm_provider is not None:
    #         try:
    #             result = self.llm_provider.classify_intent(message=message)
    #             intent = result.get("intent", "fallback")
    #             if intent in {
    #                 "query_schedule",
    #                 "campus_card_topup",
    #                 "leave_create",
    #                 "policy_qa",
    #                 "fallback",
    #                 "course_plan_generate",
    #                 "course_plan_submit",
    #             }:
    #                 return intent
    #         except Exception:
    #             pass

    #     return "fallback"

    def detect_intent(
        self,
        *,
        message: str,
        memory_context: dict | None = None,
    ) -> str:
        rule_intent = self._detect_intent_by_rules(
            message=message,
            memory_context=memory_context,
        )
        if rule_intent != "fallback":
            return rule_intent

        if self.llm_provider is not None:
            try:
                recent_messages_text = self._build_recent_messages_text(memory_context)
                result = self.llm_provider.classify_intent(
                    message=message,
                    recent_messages_text=recent_messages_text,
                )
                intent = result.get("intent", "fallback")
                if intent in {
                    "query_schedule",
                    "campus_card_topup",
                    "leave_create",
                    "policy_qa",
                    "fallback",
                    "course_plan_generate",
                    "course_plan_submit",
                    "resource_booking_generate",
                    "resource_booking_submit",
                }:
                    return intent
            except Exception:
                pass

        return "fallback"

    def _detect_intent_by_rules(
        self,
        *,
        message: str,
        memory_context: dict | None = None,
    ) -> str:
        normalized = message.strip().lower()

        policy_keywords = [
            "学生手册",
            "手册",
            "规定",
            "制度",
            "规则",
            "要求",
            "审批",
            "流程",
            "条件",
            "几天",
            "多久",
            "超过",
            "怎么办",
            "怎么处理",
            "如何处理",
            "怎么申请",
            "如何申请",
            "是否可以",
            "可不可以",
            "能不能",
            "要不要",
            "?",
            "？",
        ]

        leave_keywords = [
            "请假",
            "我要请假",
            "请病假",
            "请事假",
            "leave",
        ]

        topup_keywords = [
            "充值",
            "充钱",
            "充校园卡",
            "校园卡充值",
            "topup",
            "recharge",
        ]

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

        course_plan_keywords = [
            "选课方案",
            "帮我选课",
            "安排选课",
            "生成选课方案",
            "本学期选课",
            "最优选课",
            "课程安排方案",
            "选课",
        ]
        course_plan_submit_keywords = [
            "选方案",
            "提交方案",
            "就这个方案",
            "提交选课方案",
            "把方案提交",
        ]

        resource_booking_submit_keywords = [
            "选第一个",
            "选第二个",
            "选第三个",
            "预约这个",
            "就这个",
            "提交预约",
            "帮我预约它",
        ]
        for keyword in resource_booking_submit_keywords:
            if keyword in normalized:
                return "resource_booking_submit"

        resource_booking_keywords = [
            "预约图书馆",
            "预约自习室",
            "预约会议室",
            "预约实验室",
            "图书馆座位",
            "找自习室",
            "找会议室",
            "找实验室",
            "帮我预约",
            "我要预约",
        ]
        for keyword in resource_booking_keywords:
            if keyword in normalized:
                return "resource_booking_generate"
        for keyword in course_plan_submit_keywords:
            if keyword in normalized:
                return "course_plan_submit"
        for keyword in course_plan_keywords:
            if keyword in normalized:
                return "course_plan_generate"

        if "请假" in normalized and any(keyword in normalized for keyword in policy_keywords):
            return "policy_qa"

        if re.search(r"第[一二三四五六七八九十百千零两0-9]+(章|条)", message):
            return "policy_qa"

        if any(keyword in normalized for keyword in policy_keywords):
            return "policy_qa"


        for keyword in leave_keywords:
            if keyword in normalized:
                return "leave_create"


        for keyword in topup_keywords:
            if keyword in normalized:
                return "campus_card_topup"

        for keyword in course_plan_submit_keywords:
            if keyword in normalized:
                return "course_plan_submit"

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


        if "半天" in message:
            return 0


        chinese_day_mapping = {
            "一天": 1,
            "两天": 2,
            "二天": 2,
            "三天": 3,
            "四天": 4,
            "五天": 5,
            "六天": 6,
            "七天": 7,
            "八天": 8,
            "九天": 9,
            "十天": 10,
        }

        for text, days in chinese_day_mapping.items():
            if text in message:
                return days

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
        
    def detect_secondary_intents(self, message: str) -> list[str]:
        normalized = message.strip().lower()
        results: list[str] = []

        planning_keywords = [
            "几点出门",
            "怎么安排时间",
            "安排一下",
            "帮我规划",
            "时间安排",
            "怎么去",
            "多久出门",
        ]
        if any(keyword in normalized for keyword in planning_keywords):
            results.append("time_planning_advice")

        busyness_keywords = [
            "哪天最忙",
            "这周哪天最满",
            "什么时候最忙",
            "哪天课最多",
        ]
        if any(keyword in normalized for keyword in busyness_keywords):
            results.append("weekly_busyness_analysis")


        summary_keywords = [
            "顺便告诉我",
            "另外",
            "并且",
            "并安排",
            "顺便安排",
        ]
        if any(keyword in normalized for keyword in summary_keywords):
            if "time_planning_advice" not in results and any(
                keyword in normalized for keyword in planning_keywords
            ):
                results.append("time_planning_advice")

        return results
    
    def _build_recent_messages_text(
        self,
        memory_context: dict | None,
    ) -> str:
        if not memory_context:
            return ""

        recent_messages = memory_context.get("recent_messages", [])
        summary_text = memory_context.get("summary_text", "")

        lines: list[str] = []

        if summary_text:
            lines.append(f"会话摘要：{summary_text}")

        if recent_messages:
            lines.append("最近对话：")
            for item in recent_messages[-6:]:
                role = item.get("role", "unknown")
                content = (item.get("content") or "").strip()
                if content:
                    lines.append(f"{role}: {content}")

        return "\n".join(lines)
    
    def extract_selected_plan_index(self, message: str) -> int | None:
        normalized = message.strip().lower()

        patterns = [
            r"方案\s*([1-9]\d*)",
            r"第\s*([1-9]\d*)\s*套",
            r"第\s*([1-9]\d*)\s*个",
            r"我选\s*([1-9]\d*)",
            r"选\s*([1-9]\d*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                return int(match.group(1))

        chinese_mapping = {
            "方案一": 1,
            "方案二": 2,
            "方案三": 3,
            "第一套": 1,
            "第二套": 2,
            "第三套": 3,
            "第一个": 1,
            "第二个": 2,
            "第三个": 3,
            "我选第一套": 1,
            "我选第二套": 2,
            "我选第三套": 3,
        }

        for text, index in chinese_mapping.items():
            if text in message:
                return index

        return None
    
    def extract_resource_type(self, message: str) -> str | None:
        normalized = message.strip().lower()

        if "图书馆" in normalized or "座位" in normalized:
            return "library_seat"
        if "自习室" in normalized:
            return "study_room"
        if "会议室" in normalized:
            return "meeting_room"
        if "实验室" in normalized:
            return "lab_room"

        return None
    

    def extract_candidate_index(self, message: str) -> int | None:
        import re

        match = re.search(r"第\s*(\d+)\s*个", message)
        if match:
            return int(match.group(1))

        match = re.search(r"选\s*(\d+)", message)
        if match:
            return int(match.group(1))

        match = re.search(r"资源\s*(\d+)", message)
        if match:
            return int(match.group(1))

        return None
    

    def extract_booking_time_range(self, message: str) -> tuple[str, str] | None:
        normalized = message.strip().lower()
        now = datetime.now()

        # 默认：今天未来一小时到两小时
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=2)

        if "明天" in normalized:
            start = start + timedelta(days=1)
            end = end + timedelta(days=1)

        if "下午" in normalized:
            start = start.replace(hour=14, minute=0, second=0, microsecond=0)
            end = start.replace(hour=16, minute=0, second=0, microsecond=0)
        elif "上午" in normalized:
            start = start.replace(hour=9, minute=0, second=0, microsecond=0)
            end = start.replace(hour=11, minute=0, second=0, microsecond=0)
        elif "晚上" in normalized:
            start = start.replace(hour=19, minute=0, second=0, microsecond=0)
            end = start.replace(hour=21, minute=0, second=0, microsecond=0)

        return start.isoformat(), end.isoformat()