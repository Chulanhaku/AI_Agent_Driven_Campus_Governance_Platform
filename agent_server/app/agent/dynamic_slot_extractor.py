import re


class DynamicSlotExtractor:
    def extract_from_message(
        self,
        *,
        message: str,
        input_schema_json: dict,
    ) -> dict:
        result = {}
        normalized = message.strip()

        for field_name in input_schema_json.keys():
            value = self._extract_single_field(
                message=normalized,
                field_name=field_name,
            )
            result[field_name] = value

        return result

    def _extract_single_field(
        self,
        *,
        message: str,
        field_name: str,
    ):
        lowered = field_name.lower()

        if lowered in {"keyword", "query"}:
            # 尝试提取“帮我查 xxx”中的 xxx
            match = re.search(r"(?:查|搜索|找|查询)\s*(.+)", message)
            if match:
                return match.group(1).strip()
            return None

        if lowered in {"campus"}:
            for campus in ["主校区", "南校区", "北校区", "东校区", "西校区"]:
                if campus in message:
                    return campus
            return None

        if lowered in {"date"}:
            # 这里先做最小版
            if "今天" in message:
                return "today"
            if "明天" in message:
                return "tomorrow"
            return None

        if lowered in {"resource_type"}:
            if "图书馆" in message or "座位" in message:
                return "library_seat"
            if "自习室" in message:
                return "study_room"
            if "会议室" in message:
                return "meeting_room"
            if "实验室" in message:
                return "lab_room"
            return None

        if lowered in {"approval_type"}:
            if "请假" in message:
                return "leave_application"
            if "外出" in message:
                return "outing_application"
            if "证明" in message:
                return "certificate_request"
            return None

        return None