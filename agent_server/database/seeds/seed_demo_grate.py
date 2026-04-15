from datetime import date
from decimal import Decimal

from app.db.session import SessionLocal
from app.db.models import User, GraduationRequirement, StudentRewardPunishmentRecord


def seed_student_service_data() -> None:
    db = SessionLocal()
    try:
        student = db.query(User).filter(User.username == "student_demo").first()
        if student is None:
            raise RuntimeError("student_demo not found, please run seed_demo_user first")

        requirement_specs = [
            (
                "se_total_credits",
                "Computer Science",
                "Software Engineering",
                "2026",
                "毕业总学分要求",
                "total_credits",
                140,
                0,
                {"scope": "all_passed_courses"},
                "软件工程专业毕业至少需要140学分",
            ),
            (
                "se_required_core",
                "Computer Science",
                "Software Engineering",
                "2026",
                "专业必修学分要求",
                "required_credits",
                60,
                0,
                {
                    "course_type": ["required"],
                    "offering_department": ["Computer Science"],
                    "is_required": True,
                },
                "专业必修课至少完成60学分",
            ),
            (
                "se_elective",
                "Computer Science",
                "Software Engineering",
                "2026",
                "专业选修学分要求",
                "elective_credits",
                24,
                0,
                {
                    "course_type": ["elective"],
                    "offering_department": ["Computer Science"],
                },
                "专业选修课至少完成24学分",
            ),
            (
                "se_general",
                "Computer Science",
                "Software Engineering",
                "2026",
                "通识教育学分要求",
                "general_education_credits",
                12,
                0,
                {
                    "course_type": ["general"],
                },
                "通识课程至少完成12学分",
            ),
        ]

        for (
            requirement_code,
            department,
            major,
            grade,
            requirement_name,
            requirement_type,
            min_credits,
            min_course_count,
            rule_json,
            description,
        ) in requirement_specs:
            exists = (
                db.query(GraduationRequirement)
                .filter(
                    GraduationRequirement.department == department,
                    GraduationRequirement.major == major,
                    GraduationRequirement.grade == grade,
                    GraduationRequirement.requirement_code == requirement_code,
                )
                .first()
            )
            if exists is None:
                db.add(
                    GraduationRequirement(
                        requirement_code=requirement_code,
                        department=department,
                        major=major,
                        grade=grade,
                        requirement_name=requirement_name,
                        requirement_type=requirement_type,
                        min_credits=min_credits,
                        min_course_count=min_course_count,
                        rule_json=rule_json,
                        description=description,
                        status="active",
                    )
                )

        reward_punishment_specs = [
            (
                "reward",
                "scholarship",
                "school",
                "2025_2026学年优秀学生奖学金",
                "综合成绩排名前10%",
                Decimal("3000.00"),
                5,
                date(2026, 3, 15),
                "学生工作处",
            ),
            (
                "reward",
                "competition",
                "provincial",
                "省级程序设计竞赛三等奖",
                "参加省赛并获奖",
                None,
                3,
                date(2026, 3, 28),
                "计算机学院",
            ),
            (
                "punishment",
                "discipline",
                "warning",
                "宿舍晚归通报",
                "一次晚归登记",
                None,
                -2,
                date(2026, 2, 26),
                "学生社区管理中心",
            ),
        ]

        for (
            record_type,
            category,
            level,
            title,
            description,
            amount,
            score_delta,
            record_date,
            issuing_unit,
        ) in reward_punishment_specs:
            exists = (
                db.query(StudentRewardPunishmentRecord)
                .filter(
                    StudentRewardPunishmentRecord.user_id == student.id,
                    StudentRewardPunishmentRecord.title == title,
                )
                .first()
            )
            if exists is None:
                db.add(
                    StudentRewardPunishmentRecord(
                        user_id=student.id,
                        record_type=record_type,
                        category=category,
                        level=level,
                        title=title,
                        description=description,
                        amount=amount,
                        score_delta=score_delta,
                        record_date=record_date,
                        issuing_unit=issuing_unit,
                        status="effective",
                    )
                )

        db.commit()
        print("seed student service data success")
    except Exception as exc:
        db.rollback()
        print(f"seed student service data failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_student_service_data()