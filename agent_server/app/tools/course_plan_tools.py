from app.services.course_enrollment_service import CourseEnrollmentService
from app.services.course_plan_service import CoursePlanService
from app.tools.base import BaseTool


class GenerateCoursePlanTool(BaseTool):
    name = "generate_course_plan"
    description = "根据学生修读计划、课程权重、容量与先修要求生成候选选课方案"

    def __init__(self, course_plan_service: CoursePlanService) -> None:
        self.course_plan_service = course_plan_service

    def run(
        self,
        *,
        user_id: int,
        semester: str,
        max_plan_count: int = 3,
        **kwargs,
    ) -> dict:
        return self.course_plan_service.generate_candidate_plans(
            user_id=user_id,
            semester=semester,
            max_plan_count=max_plan_count,
        )


class SubmitCoursePlanTool(BaseTool):
    name = "submit_course_plan"
    description = "提交已选中的候选选课方案，该工具只应在用户确认后调用"

    def __init__(self, course_enrollment_service: CourseEnrollmentService) -> None:
        self.course_enrollment_service = course_enrollment_service

    def run(
        self,
        *,
        user_id: int,
        semester: str,
        selected_plan: dict,
        **kwargs,
    ) -> dict:
        return self.course_enrollment_service.submit_generated_plan(
            user_id=user_id,
            semester=semester,
            selected_plan=selected_plan,
        )