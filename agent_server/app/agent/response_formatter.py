class ResponseFormatter:
    def format(self, *, intent: str, result: dict) -> str:
        if intent == "query_schedule" and result.get("success"):
            items = result.get("items", [])
            total = result.get("total", 0)

            if total == 0:
                return "我查到了你的课表数据，但当前条件下没有课程安排。"

            lines = [f"我查到了 {total} 条课表记录："]
            for item in items:
                course = item["course"]
                lines.append(
                    f"星期{item['weekday']} "
                    f"{item['start_time']}-{item['end_time']} "
                    f"{course['course_name']} "
                    f"@ {item['classroom'] or '未填写教室'}"
                )

            return "\n".join(lines)

        if intent == "campus_card_topup" and result.get("requires_confirmation"):
            amount = result.get("amount")
            action_id = result.get("action_id")
            return f"即将为你的校园卡充值 {amount} 元。请确认本次操作。待确认动作 ID：{action_id}"

        if intent == "campus_card_topup" and result.get("success"):
            data = result["data"]
            return (
                f"校园卡充值成功。\n"
                f"充值金额：{data['amount']} 元\n"
                f"当前余额：{data['balance_after']} 元\n"
                f"交易号：{data['txn_id']}"
            )

        return "我已经收到你的消息，但当前还没有匹配到具体业务能力，所以先进入普通回复模式。"