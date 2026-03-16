# from collections import defaultdict
# from itertools import combinations

# from app.db.models import CourseSection, StudentCompletedCourse, StudentCoursePlan


# class CoursePlanOptimizer:
#     def generate_candidate_plans(
#         self,
#         *,
#         sections: list[CourseSection],
#         completed_courses: list[StudentCompletedCourse],
#         active_plan: StudentCoursePlan | None,
#         prerequisites: list,
#         max_plan_count: int = 3,
#     ) -> list[dict]:
#         passed_course_ids = {
#             item.course_id
#             for item in completed_courses
#             if item.passed
#         }

#         prerequisite_map = self._build_prerequisite_map(prerequisites)
#         grouped_sections = self._group_sections_by_course(sections)

#         candidate_course_ids = self._filter_candidate_course_ids(
#             grouped_sections=grouped_sections,
#             passed_course_ids=passed_course_ids,
#             prerequisite_map=prerequisite_map,
#         )

#         candidate_course_ids = self._sort_candidate_course_ids(
#             candidate_course_ids=candidate_course_ids,
#             grouped_sections=grouped_sections,
#         )

#         max_credits = active_plan.max_credits if active_plan else 18

#         plans: list[dict] = []
#         max_course_count = min(len(candidate_course_ids), 6)

#         for course_count in range(1, max_course_count + 1):
#             for course_id_combo in combinations(candidate_course_ids, course_count):
#                 section_combo = self._pick_best_non_conflicting_sections(
#                     course_ids=list(course_id_combo),
#                     grouped_sections=grouped_sections,
#                 )
#                 if not section_combo:
#                     continue

#                 total_credits = sum(
#                     int(section.course.credits or 0)
#                     for section in section_combo
#                 )
#                 if total_credits > max_credits:
#                     continue

#                 score, reasons = self._score_plan(
#                     sections=section_combo,
#                     active_plan=active_plan,
#                 )

#                 plan = {
#                     "course_count": len(section_combo),
#                     "total_credits": total_credits,
#                     "score": score,
#                     "reasons": reasons,
#                     "items": [
#                         {
#                             "course_id": section.course.id,
#                             "course_code": section.course.course_code,
#                             "course_name": section.course.course_name,
#                             "credits": int(section.course.credits or 0),
#                             "section_id": section.id,
#                             "section_code": section.section_code,
#                             "weekday": section.weekday,
#                             "start_time": section.start_time.strftime("%H:%M:%S"),
#                             "end_time": section.end_time.strftime("%H:%M:%S"),
#                             "classroom": section.classroom,
#                             "capacity": section.capacity,
#                             "enrolled_count": section.enrolled_count,
#                             "is_required": bool(section.course.is_required),
#                             "weight": float(section.course.weight or 0),
#                         }
#                         for section in section_combo
#                     ],
#                 }

#                 plans.append(plan)

#         plans.sort(
#             key=lambda x: (
#                 x["score"],
#                 x["total_credits"],
#                 x["course_count"],
#             ),
#             reverse=True,
#         )

#         deduped_plans = self._deduplicate_plans(plans)
#         return deduped_plans[:max_plan_count]

#     def _build_prerequisite_map(self, prerequisites: list) -> dict[int, list[int]]:
#         result: dict[int, list[int]] = defaultdict(list)
#         for item in prerequisites:
#             result[item.course_id].append(item.prerequisite_course_id)
#         return result

#     def _group_sections_by_course(
#         self,
#         sections: list[CourseSection],
#     ) -> dict[int, list[CourseSection]]:
#         grouped: dict[int, list[CourseSection]] = defaultdict(list)
#         for section in sections:
#             if section.enrolled_count >= section.capacity:
#                 continue
#             grouped[section.course_id].append(section)
#         return grouped

#     def _filter_candidate_course_ids(
#         self,
#         *,
#         grouped_sections: dict[int, list[CourseSection]],
#         passed_course_ids: set[int],
#         prerequisite_map: dict[int, list[int]],
#     ) -> list[int]:
#         result: list[int] = []

#         for course_id, sections in grouped_sections.items():
#             if not sections:
#                 continue

#             if course_id in passed_course_ids:
#                 continue

#             required_prereqs = prerequisite_map.get(course_id, [])
#             if required_prereqs:
#                 if not all(prereq_id in passed_course_ids for prereq_id in required_prereqs):
#                     continue

#             result.append(course_id)

#         return result

#     def _sort_candidate_course_ids(
#         self,
#         *,
#         candidate_course_ids: list[int],
#         grouped_sections: dict[int, list[CourseSection]],
#     ) -> list[int]:
#         def sort_key(course_id: int):
#             first_section = grouped_sections[course_id][0]
#             course = first_section.course
#             return (
#                 1 if course.is_required else 0,
#                 float(course.weight or 0),
#                 int(course.credits or 0),
#             )

#         return sorted(candidate_course_ids, key=sort_key, reverse=True)

#     def _pick_best_non_conflicting_sections(
#         self,
#         *,
#         course_ids: list[int],
#         grouped_sections: dict[int, list[CourseSection]],
#     ) -> list[CourseSection] | None:
#         selected: list[CourseSection] = []

#         for course_id in course_ids:
#             sections = grouped_sections.get(course_id, [])
#             best_section = None
#             best_score = None

#             for section in sections:
#                 if self._has_time_conflict(selected, section):
#                     continue

#                 section_score = self._score_section(section)
#                 if best_section is None or section_score > best_score:
#                     best_section = section
#                     best_score = section_score

#             if best_section is None:
#                 return None

#             selected.append(best_section)

#         return selected

#     def _score_section(self, section: CourseSection) -> float:
#         remain_capacity = section.capacity - section.enrolled_count
#         course_weight = float(section.course.weight or 0)
#         required_bonus = 100 if section.course.is_required else 0
#         capacity_bonus = min(remain_capacity, 50)
#         return required_bonus + course_weight * 10 + capacity_bonus

#     def _has_time_conflict(
#         self,
#         selected_sections: list[CourseSection],
#         new_section: CourseSection,
#     ) -> bool:
#         for section in selected_sections:
#             if section.weekday != new_section.weekday:
#                 continue

#             if (
#                 new_section.start_time < section.end_time
#                 and new_section.end_time > section.start_time
#             ):
#                 return True

#         return False

#     def _score_plan(
#         self,
#         *,
#         sections: list[CourseSection],
#         active_plan: StudentCoursePlan | None,
#     ) -> tuple[float, list[str]]:
#         score = 0.0
#         reasons: list[str] = []

#         required_count = sum(1 for section in sections if section.course.is_required)
#         total_weight = sum(float(section.course.weight or 0) for section in sections)
#         total_credits = sum(int(section.course.credits or 0) for section in sections)

#         score += required_count * 100
#         score += total_weight * 10
#         score += total_credits * 2

#         if required_count > 0:
#             reasons.append(f"包含 {required_count} 门高优先级/必修课程")

#         reasons.append(f"总学分为 {total_credits}，课程权重累计 {total_weight:.2f}")

#         if active_plan:
#             avoid_days = set(active_plan.avoid_days_json or [])
#             preferred_days = set(active_plan.preferred_days_json or [])

#             avoid_penalty = 0
#             preferred_bonus = 0

#             for section in sections:
#                 if section.weekday in avoid_days:
#                     avoid_penalty += 20
#                 if section.weekday in preferred_days:
#                     preferred_bonus += 10

#                 if active_plan.avoid_morning and section.start_time.hour < 12:
#                     avoid_penalty += 10

#                 if active_plan.avoid_evening and section.start_time.hour >= 18:
#                     avoid_penalty += 10

#             score += preferred_bonus
#             score -= avoid_penalty

#             if preferred_bonus > 0:
#                 reasons.append("较好匹配学生的偏好上课日期")
#             if avoid_penalty > 0:
#                 reasons.append("部分课程触及学生规避时间段，因此有一定扣分")

#         weekday_distribution: dict[int, int] = defaultdict(int)
#         for section in sections:
#             weekday_distribution[section.weekday] += 1

#         if weekday_distribution:
#             max_day_load = max(weekday_distribution.values())
#             if max_day_load >= 3:
#                 score -= 15
#                 reasons.append("存在单日课程较密集情况")
#             else:
#                 reasons.append("课程分布较均衡")

#         return score, reasons

#     def _deduplicate_plans(self, plans: list[dict]) -> list[dict]:
#         seen = set()
#         result = []

#         for plan in plans:
#             signature = tuple(
#                 sorted(
#                     (item["course_id"], item["section_id"])
#                     for item in plan["items"]
#                 )
#             )
#             if signature in seen:
#                 continue
#             seen.add(signature)
#             result.append(plan)

#         return result

from collections import defaultdict
from itertools import combinations

from app.db.models import CourseSection, StudentCompletedCourse, StudentCoursePlan


class CoursePlanOptimizer:
    def generate_candidate_plans(
        self,
        *,
        sections: list[CourseSection],
        completed_courses: list[StudentCompletedCourse],
        prerequisites: list,
        active_plan: StudentCoursePlan | None,
        max_plan_count: int = 3,
    ) -> list[dict]:
        passed_course_ids = {
            item.course_id
            for item in completed_courses
            if item.passed
        }

        prerequisite_map = self._build_prerequisite_map(prerequisites)
        grouped_sections = self._group_sections_by_course(sections)

        candidate_course_ids = self._filter_candidate_course_ids(
            grouped_sections=grouped_sections,
            passed_course_ids=passed_course_ids,
            prerequisite_map=prerequisite_map,
        )

        candidate_course_ids = self._sort_candidate_course_ids(
            candidate_course_ids=candidate_course_ids,
            grouped_sections=grouped_sections,
        )

        max_credits = active_plan.max_credits if active_plan else 18

        plans: list[dict] = []
        max_course_count = min(len(candidate_course_ids), 6)

        for course_count in range(1, max_course_count + 1):
            for course_id_combo in combinations(candidate_course_ids, course_count):
                section_combo = self._pick_best_non_conflicting_sections(
                    course_ids=list(course_id_combo),
                    grouped_sections=grouped_sections,
                )
                if not section_combo:
                    continue

                total_credits = sum(
                    int(section.course.credits or 0)
                    for section in section_combo
                )
                if total_credits > max_credits:
                    continue

                score, reasons = self._score_plan(
                    sections=section_combo,
                    active_plan=active_plan,
                    passed_course_ids=passed_course_ids,
                    prerequisite_map=prerequisite_map,
                )

                plan = {
                    "course_count": len(section_combo),
                    "total_credits": total_credits,
                    "score": score,
                    "reasons": reasons,
                    "items": [
                        {
                            "course_id": section.course.id,
                            "course_code": section.course.course_code,
                            "course_name": section.course.course_name,
                            "credits": int(section.course.credits or 0),
                            "section_id": section.id,
                            "section_code": section.section_code,
                            "weekday": section.weekday,
                            "start_time": section.start_time.strftime("%H:%M:%S"),
                            "end_time": section.end_time.strftime("%H:%M:%S"),
                            "classroom": section.classroom,
                            "capacity": section.capacity,
                            "enrolled_count": section.enrolled_count,
                            "is_required": bool(section.course.is_required),
                            "weight": float(section.course.weight or 0),
                        }
                        for section in section_combo
                    ],
                }

                plans.append(plan)

        plans.sort(
            key=lambda x: (
                x["score"],
                x["total_credits"],
                x["course_count"],
            ),
            reverse=True,
        )

        deduped_plans = self._deduplicate_plans(plans)
        return deduped_plans[:max_plan_count]

    def _build_prerequisite_map(self, prerequisites: list) -> dict[int, dict[str, list[int]]]:
        result: dict[int, dict[str, list[int]]] = defaultdict(
            lambda: {
                "required": [],
                "recommended": [],
            }
        )

        for item in prerequisites:
            rule_type = (item.rule_type or "required").lower()
            if rule_type == "recommended":
                result[item.course_id]["recommended"].append(item.prerequisite_course_id)
            else:
                result[item.course_id]["required"].append(item.prerequisite_course_id)

        return result

    def _group_sections_by_course(
        self,
        sections: list[CourseSection],
    ) -> dict[int, list[CourseSection]]:
        grouped: dict[int, list[CourseSection]] = defaultdict(list)
        for section in sections:
            if section.enrolled_count >= section.capacity:
                continue
            grouped[section.course_id].append(section)
        return grouped

    def _filter_candidate_course_ids(
        self,
        *,
        grouped_sections: dict[int, list[CourseSection]],
        passed_course_ids: set[int],
        prerequisite_map: dict[int, dict[str, list[int]]],
    ) -> list[int]:
        result: list[int] = []

        for course_id, sections in grouped_sections.items():
            if not sections:
                continue

            if course_id in passed_course_ids:
                continue

            prereq_info = prerequisite_map.get(
                course_id,
                {
                    "required": [],
                    "recommended": [],
                },
            )
            required_prereqs = prereq_info.get("required", [])

            if required_prereqs:
                if not all(prereq_id in passed_course_ids for prereq_id in required_prereqs):
                    continue

            result.append(course_id)

        return result

    def _sort_candidate_course_ids(
        self,
        *,
        candidate_course_ids: list[int],
        grouped_sections: dict[int, list[CourseSection]],
    ) -> list[int]:
        def sort_key(course_id: int):
            first_section = grouped_sections[course_id][0]
            course = first_section.course
            return (
                1 if course.is_required else 0,
                float(course.weight or 0),
                int(course.credits or 0),
            )

        return sorted(candidate_course_ids, key=sort_key, reverse=True)

    def _pick_best_non_conflicting_sections(
        self,
        *,
        course_ids: list[int],
        grouped_sections: dict[int, list[CourseSection]],
    ) -> list[CourseSection] | None:
        selected: list[CourseSection] = []

        for course_id in course_ids:
            sections = grouped_sections.get(course_id, [])
            best_section = None
            best_score = None

            for section in sections:
                if self._has_time_conflict(selected, section):
                    continue

                section_score = self._score_section(section)
                if best_section is None or section_score > best_score:
                    best_section = section
                    best_score = section_score

            if best_section is None:
                return None

            selected.append(best_section)

        return selected

    def _score_section(self, section: CourseSection) -> float:
        remain_capacity = section.capacity - section.enrolled_count
        course_weight = float(section.course.weight or 0)
        required_bonus = 100 if section.course.is_required else 0
        capacity_bonus = min(remain_capacity, 50)
        return required_bonus + course_weight * 10 + capacity_bonus

    def _has_time_conflict(
        self,
        selected_sections: list[CourseSection],
        new_section: CourseSection,
    ) -> bool:
        for section in selected_sections:
            if section.weekday != new_section.weekday:
                continue

            if (
                new_section.start_time < section.end_time
                and new_section.end_time > section.start_time
            ):
                return True

        return False

    def _score_plan(
        self,
        *,
        sections: list[CourseSection],
        active_plan: StudentCoursePlan | None,
        passed_course_ids: set[int],
        prerequisite_map: dict[int, dict[str, list[int]]],
    ) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        required_count = sum(1 for section in sections if section.course.is_required)
        total_weight = sum(float(section.course.weight or 0) for section in sections)
        total_credits = sum(int(section.course.credits or 0) for section in sections)

        score += required_count * 100
        score += total_weight * 10
        score += total_credits * 2

        if required_count > 0:
            reasons.append(f"包含 {required_count} 门高优先级/必修课程")

        reasons.append(f"总学分为 {total_credits}，课程权重累计 {total_weight:.2f}")

        # 推荐先修：只加分，不做硬拦截
        recommended_match_count = 0
        for section in sections:
            prereq_info = prerequisite_map.get(section.course.id, {})
            recommended_prereqs = prereq_info.get("recommended", [])
            if recommended_prereqs and all(
                prereq_id in passed_course_ids for prereq_id in recommended_prereqs
            ):
                recommended_match_count += 1

        if recommended_match_count > 0:
            score += recommended_match_count * 15
            reasons.append(f"满足 {recommended_match_count} 门课程的推荐先修条件")

        if active_plan:
            avoid_days = set(active_plan.avoid_days_json or [])
            preferred_days = set(active_plan.preferred_days_json or [])

            avoid_penalty = 0
            preferred_bonus = 0

            for section in sections:
                if section.weekday in avoid_days:
                    avoid_penalty += 20
                if section.weekday in preferred_days:
                    preferred_bonus += 10

                if active_plan.avoid_morning and section.start_time.hour < 12:
                    avoid_penalty += 10

                if active_plan.avoid_evening and section.start_time.hour >= 18:
                    avoid_penalty += 10

            score += preferred_bonus
            score -= avoid_penalty

            if preferred_bonus > 0:
                reasons.append("较好匹配学生的偏好上课日期")
            if avoid_penalty > 0:
                reasons.append("部分课程触及学生规避时间段，因此有一定扣分")

        weekday_distribution: dict[int, int] = defaultdict(int)
        for section in sections:
            weekday_distribution[section.weekday] += 1

        if weekday_distribution:
            max_day_load = max(weekday_distribution.values())
            if max_day_load >= 3:
                score -= 15
                reasons.append("存在单日课程较密集情况")
            else:
                reasons.append("课程分布较均衡")

        return score, reasons

    def _deduplicate_plans(self, plans: list[dict]) -> list[dict]:
        seen = set()
        result = []

        for plan in plans:
            signature = tuple(
                sorted(
                    (item["course_id"], item["section_id"])
                    for item in plan["items"]
                )
            )
            if signature in seen:
                continue
            seen.add(signature)
            result.append(plan)

        return result