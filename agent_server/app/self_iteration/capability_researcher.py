from app.tools.db_data_search_tool import DbDataSearchTool
from app.tools.db_schema_search_tool import DbSchemaSearchTool
from app.tools.web_research_tool import WebResearchTool


class CapabilityResearcher:
    def __init__(
        self,
        web_research_tool: WebResearchTool,
        db_schema_search_tool: DbSchemaSearchTool,
        db_data_search_tool: DbDataSearchTool,
    ) -> None:
        self.web_research_tool = web_research_tool
        self.db_schema_search_tool = db_schema_search_tool
        self.db_data_search_tool = db_data_search_tool

    def research(
        self,
        *,
        user_message: str,
    ) -> dict:
        keywords = self._extract_keywords(user_message)

        web_findings = self.web_research_tool.run(
            query=user_message,
            max_results=5,
        )

        schema_findings = self.db_schema_search_tool.run(
            keywords=keywords,
        )

        db_findings = []
        for table_name in self._infer_candidate_tables(keywords):
            result = self.db_data_search_tool.run(
                table_name=table_name,
                keyword=user_message,
                limit=3,
            )
            if result.get("success"):
                db_findings.append(result)

        return {
            "web_findings": web_findings,
            "schema_findings": schema_findings,
            "db_findings": db_findings,
            "summary": self._build_summary(
                web_findings=web_findings,
                schema_findings=schema_findings,
                db_findings=db_findings,
            ),
        }

    def _extract_keywords(self, user_message: str) -> list[str]:
        candidates = [
            "校车",
            "班车",
            "羽毛球馆",
            "成绩单",
            "导出",
            "实习证明",
            "证明",
            "场馆",
            "体育馆",
            "预约",
            "课表",
            "审批",
        ]
        return [item for item in candidates if item in user_message]

    def _infer_candidate_tables(self, keywords: list[str]) -> list[str]:
        mapping = {
            "课表": ["courses", "schedule_entries", "course_sections"],
            "审批": ["approval_templates", "zero_form_approval_requests"],
            "预约": ["resources", "resource_bookings"],
            "证明": ["approval_templates", "zero_form_approval_requests"],
        }

        results = []
        for keyword in keywords:
            results.extend(mapping.get(keyword, []))

        return list(dict.fromkeys(results))

    def _build_summary(
        self,
        *,
        web_findings: dict,
        schema_findings: dict,
        db_findings: list[dict],
    ) -> str:
        web_count = len(web_findings.get("results", [])) if web_findings.get("success") else 0
        schema_count = len(schema_findings.get("results", [])) if schema_findings.get("success") else 0
        db_count = sum(len(item.get("results", [])) for item in db_findings)

        return (
            f"web results={web_count}, "
            f"schema tables={schema_count}, "
            f"db rows={db_count}"
        )