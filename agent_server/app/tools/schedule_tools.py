from app.services.schedule_service import ScheduleService
from app.tools.base import BaseTool


class QueryMyScheduleTool(BaseTool):
    name = "query_my_schedule"
    description = "查询当前登录用户的课表，可按学期和星期过滤"

    def __init__(self, schedule_service: ScheduleService) -> None:
        self.schedule_service = schedule_service

    def run(
        self,
        *,
        user_id: int,
        semester: str | None = None,
        weekday: int | None = None,
    ) -> dict:
        items = self.schedule_service.list_my_schedule(
            user_id=user_id,
            semester=semester,
            weekday=weekday,
        )

        result_items = []
        for item in items:
            result_items.append(
                {
                    "id": item.id,
                    "weekday": item.weekday,
                    "start_time": item.start_time.strftime("%H:%M:%S"),
                    "end_time": item.end_time.strftime("%H:%M:%S"),
                    "classroom": item.classroom,
                    "week_range": item.week_range,
                    "semester": item.semester,
                    "course": {
                        "id": item.course.id,
                        "course_code": item.course.course_code,
                        "course_name": item.course.course_name,
                        "semester": item.course.semester,
                    },
                }
            )

        return {
            "success": True,
            "tool_name": self.name,
            "items": result_items,
            "total": len(result_items),
        }