import re
from datetime import datetime


class SemesterUtils:
    @staticmethod
    def get_current_semester() -> str:
        now = datetime.now()
        year = now.year
        month = now.month

        if 2 <= month <= 7:
            return f"{year}-spring"

        if month == 1:
            return f"{year - 1}-fall"

        return f"{year}-fall"

    @staticmethod
    def get_next_semester(current_semester: str | None = None) -> str:
        current = current_semester or SemesterUtils.get_current_semester()
        year_str, term = current.split("-")
        year = int(year_str)

        if term == "spring":
            return f"{year}-fall"

        return f"{year + 1}-spring"

    @staticmethod
    def normalize_semester_text(text: str) -> str:
        return (
            text.strip()
            .lower()
            .replace(" ", "")
            .replace("　", "")
            .replace("学期", "")
        )

    @staticmethod
    def parse_semester_from_message(message: str) -> str | None:
        normalized = SemesterUtils.normalize_semester_text(message)

        if "本学期" in normalized:
            return SemesterUtils.get_current_semester()

        if "下学期" in normalized or "下个学期" in normalized:
            return SemesterUtils.get_next_semester()

        spring_match = re.search(r"(20\d{2})年?(春|春季)", normalized)
        if spring_match:
            year = spring_match.group(1)
            return f"{year}-spring"

        fall_match = re.search(r"(20\d{2})年?(秋|秋季)", normalized)
        if fall_match:
            year = fall_match.group(1)
            return f"{year}-fall"

        eng_match = re.search(r"(20\d{2})-(spring|fall)", normalized)
        if eng_match:
            year = eng_match.group(1)
            term = eng_match.group(2)
            return f"{year}-{term}"

        return None

    @staticmethod
    def format_semester_for_human(semester: str | None) -> str:
        if not semester:
            return "未指定学期"

        year, term = semester.split("-")
        if term == "spring":
            return f"{year} 年春季学期"
        if term == "fall":
            return f"{year} 年秋季学期"
        return semester