# from app.db.repositories.completed_course_repository import CompletedCourseRepository
# from app.db.repositories.course_prerequisite_repository import CoursePrerequisiteRepository
# from app.db.repositories.course_section_repository import CourseSectionRepository
# from app.db.repositories.student_course_plan_repository import StudentCoursePlanRepository
# from app.optimizer.course_plan_optimizer import CoursePlanOptimizer


# class CoursePlanService:
#     def __init__(
#         self,
#         course_section_repository: CourseSectionRepository,
#         student_course_plan_repository: StudentCoursePlanRepository,
#         completed_course_repository: CompletedCourseRepository,
#         course_prerequisite_repository: CoursePrerequisiteRepository,
#     ) -> None:
#         self.course_section_repository = course_section_repository
#         self.student_course_plan_repository = student_course_plan_repository
#         self.completed_course_repository = completed_course_repository
#         self.course_prerequisite_repository = course_prerequisite_repository
#         self.optimizer = CoursePlanOptimizer()

#     def generate_candidate_plans(
#         self,
#         *,
#         user_id: int,
#         semester: str,
#         max_plan_count: int = 3,
#     ) -> dict:
#         active_plan = self.student_course_plan_repository.get_active_plan_by_user_id_and_semester(
#             user_id=user_id,
#             semester=semester,
#         )
#         completed_courses = self.completed_course_repository.list_passed_courses_by_user_id(
#             user_id=user_id,
#         )
#         sections = self.course_section_repository.list_open_sections_by_semester(
#             semester=semester,
#         )
#         prerequisites = self.course_prerequisite_repository.list_all()

#         plans = self.optimizer.generate_candidate_plans(
#             sections=sections,
#             completed_courses=completed_courses,
#             active_plan=active_plan,
#             prerequisites=prerequisites,
#             max_plan_count=max_plan_count,
#         )

#         return {
#             "success": True,
#             "semester": semester,
#             "plan_count": len(plans),
#             "plans": plans,
#             "student_preferences": {
#                 "max_credits": active_plan.max_credits if active_plan else 18,
#                 "preferred_days_json": active_plan.preferred_days_json if active_plan else None,
#                 "avoid_days_json": active_plan.avoid_days_json if active_plan else None,
#                 "avoid_morning": active_plan.avoid_morning if active_plan else False,
#                 "avoid_evening": active_plan.avoid_evening if active_plan else False,
#             },
#         }
#version 2
# from app.db.repositories.completed_course_repository import CompletedCourseRepository
# from app.db.repositories.course_prerequisite_repository import CoursePrerequisiteRepository
# from app.db.repositories.course_section_repository import CourseSectionRepository
# from app.db.repositories.student_course_plan_repository import StudentCoursePlanRepository
# from app.optimizer.course_plan_optimizer import CoursePlanOptimizer


# class CoursePlanService:
#     def __init__(
#         self,
#         course_section_repository: CourseSectionRepository,
#         student_course_plan_repository: StudentCoursePlanRepository,
#         completed_course_repository: CompletedCourseRepository,
#         course_prerequisite_repository: CoursePrerequisiteRepository,
#     ) -> None:
#         self.course_section_repository = course_section_repository
#         self.student_course_plan_repository = student_course_plan_repository
#         self.completed_course_repository = completed_course_repository
#         self.course_prerequisite_repository = course_prerequisite_repository
#         self.optimizer = CoursePlanOptimizer()

#     def generate_candidate_plans(
#         self,
#         *,
#         user_id: int,
#         semester: str,
#         max_plan_count: int = 3,
#     ) -> dict:
#         active_plan = self.student_course_plan_repository.get_active_plan_by_user_id_and_semester(
#             user_id=user_id,
#             semester=semester,
#         )
#         completed_courses = self.completed_course_repository.list_passed_courses_by_user_id(
#             user_id=user_id,
#         )
#         sections = self.course_section_repository.list_open_sections_by_semester(
#             semester=semester,
#         )
#         prerequisites = self.course_prerequisite_repository.list_all()

#         plans = self.optimizer.generate_candidate_plans(
#             sections=sections,
#             completed_courses=completed_courses,
#             prerequisites=prerequisites,
#             active_plan=active_plan,
#             max_plan_count=max_plan_count,
#         )

#         return {
#             "success": True,
#             "semester": semester,
#             "plan_count": len(plans),
#             "plans": plans,
#             "student_preferences": {
#                 "max_credits": active_plan.max_credits if active_plan else 18,
#                 "preferred_days_json": active_plan.preferred_days_json if active_plan else None,
#                 "avoid_days_json": active_plan.avoid_days_json if active_plan else None,
#                 "avoid_morning": active_plan.avoid_morning if active_plan else False,
#                 "avoid_evening": active_plan.avoid_evening if active_plan else False,
#             },
#         }


from app.db.repositories.completed_course_repository import CompletedCourseRepository
from app.db.repositories.course_prerequisite_repository import CoursePrerequisiteRepository
from app.db.repositories.course_section_repository import CourseSectionRepository
from app.db.repositories.student_course_plan_repository import StudentCoursePlanRepository
from app.optimizer.course_plan_optimizer import CoursePlanOptimizer


class CoursePlanService:
    def __init__(
        self,
        course_section_repository: CourseSectionRepository,
        student_course_plan_repository: StudentCoursePlanRepository,
        completed_course_repository: CompletedCourseRepository,
        course_prerequisite_repository: CoursePrerequisiteRepository,
    ) -> None:
        self.course_section_repository = course_section_repository
        self.student_course_plan_repository = student_course_plan_repository
        self.completed_course_repository = completed_course_repository
        self.course_prerequisite_repository = course_prerequisite_repository
        self.optimizer = CoursePlanOptimizer()

    def generate_candidate_plans(
        self,
        *,
        user_id: int,
        semester: str,
        max_plan_count: int = 3,
    ) -> dict:
        active_plan = self.student_course_plan_repository.get_active_plan_by_user_id_and_semester(
            user_id=user_id,
            semester=semester,
        )
        completed_courses = self.completed_course_repository.list_passed_courses_by_user_id(
            user_id=user_id,
        )
        sections = self.course_section_repository.list_open_sections_by_semester(
            semester=semester,
        )
        prerequisites = self.course_prerequisite_repository.list_all()

        plans = self.optimizer.generate_candidate_plans(
            sections=sections,
            completed_courses=completed_courses,
            prerequisites=prerequisites,
            active_plan=active_plan,
            max_plan_count=max_plan_count,
        )

        return {
            "success": True,
            "semester": semester,
            "plan_count": len(plans),
            "plans": plans,
            "student_preferences": {
                "max_credits": active_plan.max_credits if active_plan else 18,
                "preferred_days_json": active_plan.preferred_days_json if active_plan else None,
                "avoid_days_json": active_plan.avoid_days_json if active_plan else None,
                "avoid_morning": active_plan.avoid_morning if active_plan else False,
                "avoid_evening": active_plan.avoid_evening if active_plan else False,
            },
        }