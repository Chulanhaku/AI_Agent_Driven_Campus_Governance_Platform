class ResponseFormatter:
    def format(self, *, intent: str, result: dict) -> str:
        if intent == "query_schedule" and result.get("success"):
            items = result.get("items", [])
            total = result.get("total", 0)

            if total == 0:
                return "当前条件下没有课程安排。"

            lines = [f"共查询到 {total} 条课表记录："]
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

        if intent == "leave_create" and result.get("requires_confirmation"):
            action_id = result.get("action_id")
            days = result.get("days")
            reason = result.get("reason")
            return (
                f"即将提交请假申请。\n"
                f"请假天数：{days} 天\n"
                f"原因：{reason}\n"
                f"请确认本次操作。待确认动作 ID：{action_id}"
            )

        if intent == "leave_create" and result.get("success"):
            data = result["data"]
            return (
                f"请假申请提交成功。\n"
                f"请假单号：{data['leave_request_id']}\n"
                f"请假类型：{data['leave_type']}\n"
                f"起始日期：{data['start_date']}\n"
                f"结束日期：{data['end_date']}\n"
                f"状态：{data['status']}"
            )

        if intent == "course_plan_generate" and result.get("success"):
            plans = result.get("plans", [])
            if not plans:
                return "当前没有生成可行的选课方案。,test1"

            lines = [f"共生成 {len(plans)} 套候选选课方案："]
            for idx, plan in enumerate(plans, start=1):
                course_names = [item["course_name"] for item in plan["items"]]
                lines.append(
                    f"方案 {idx}："
                    f"总学分 {plan['total_credits']}，"
                    f"课程数 {plan['course_count']}，"
                    f"评分 {plan['score']:.2f}；"
                    f"课程包括：{', '.join(course_names)}。"
                )
                if plan.get("reasons"):
                    lines.append(f"推荐理由：{'；'.join(plan['reasons'])}")

            return "\n".join(lines)
        

        if intent == "course_plan_submit" and result.get("requires_confirmation"):
            action_id = result.get("action_id")
            selected_plan_index = result.get("selected_plan_index")
            return (
                f"即将提交选课方案 {selected_plan_index}。\n"
                f"请确认本次操作。待确认动作 ID：{action_id}"
            )

        if intent == "course_plan_submit" and result.get("success"):
            return (
                f"选课方案提交成功。\n"
                f"提交单号：{result['request_id']}\n"
                f"学期：{result['semester']}\n"
                f"提交课程数：{result['submitted_course_count']}\n"
                f"状态：{result['status']}"
            )
        
        if intent == "policy_qa" and result.get("success"):
            items = result.get("items", [])
            if not items:
                return "没有检索到相关制度材料。"

            lines = ["检索到以下制度材料："]
            for item in items:
                lines.append(f"[{item['filename']}] {item['content']}")
            return "\n\n".join(lines)
        
        if intent == "send_notification" and result.get("success"):
            data = result.get("data", {})
            return (
                f"通知发送成功！\n"
                f"接收用户ID：{data.get('user_id')}\n"
                f"消息内容：{data.get('message')}"
            )

        return "当前没有可用的工具结果摘要。"