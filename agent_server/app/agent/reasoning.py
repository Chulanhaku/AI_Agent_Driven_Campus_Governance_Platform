class ReasoningEngine:
    def reason(
        self,
        *,
        goal: str,
        tool_results: dict,
        user_message: str,
    ) -> dict:
        if goal == "time_planning_advice":
            return self._build_time_planning_advice(
                tool_results=tool_results,
            )

        if goal == "weekly_busyness_analysis":
            return self._build_weekly_busyness_analysis(
                tool_results=tool_results,
            )

        return {
            "success": False,
            "goal": goal,
            "message": "Unsupported reasoning goal",
        }

    def _build_time_planning_advice(self, *, tool_results: dict) -> dict:
        schedule_result = tool_results.get("query_my_schedule")
        if not schedule_result or not schedule_result.get("success"):
            return {
                "success": False,
                "goal": "time_planning_advice",
                "message": "Schedule data is not available",
            }

        items = schedule_result.get("items", [])
        advice_items = []

        for item in items:
            start_time = item["start_time"]
            hour, minute, _ = start_time.split(":")
            hour = int(hour)
            minute = int(minute)

            total_minutes = hour * 60 + minute
            suggested_departure = total_minutes - 40
            depart_hour = suggested_departure // 60
            depart_minute = suggested_departure % 60

            advice_items.append(
                {
                    "weekday": item["weekday"],
                    "course_name": item["course"]["course_name"],
                    "classroom": item["classroom"],
                    "class_start_time": start_time,
                    "suggested_departure_time": f"{depart_hour:02d}:{depart_minute:02d}",
                    "advice_note": "按上课前约 40 分钟出门估算，适合校内步行或常规通勤场景。",
                }
            )

        return {
            "success": True,
            "goal": "time_planning_advice",
            "items": advice_items,
        }

    def _build_weekly_busyness_analysis(self, *, tool_results: dict) -> dict:
        schedule_result = tool_results.get("query_my_schedule")
        if not schedule_result or not schedule_result.get("success"):
            return {
                "success": False,
                "goal": "weekly_busyness_analysis",
                "message": "Schedule data is not available",
            }

        items = schedule_result.get("items", [])
        weekday_count: dict[int, int] = {}

        for item in items:
            weekday = item["weekday"]
            weekday_count[weekday] = weekday_count.get(weekday, 0) + 1

        if not weekday_count:
            return {
                "success": True,
                "goal": "weekly_busyness_analysis",
                "busiest_weekday": None,
                "weekday_count": {},
            }

        busiest_weekday = max(weekday_count, key=weekday_count.get)

        return {
            "success": True,
            "goal": "weekly_busyness_analysis",
            "busiest_weekday": busiest_weekday,
            "weekday_count": weekday_count,
        }