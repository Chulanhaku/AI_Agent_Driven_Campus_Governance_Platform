from sqlalchemy import MetaData, Table, String, cast, or_, select
from sqlalchemy.orm import Session

from app.tools.web_research_tool import WebResearchTool


class DynamicToolExecutor:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.metadata = MetaData()
        self.web_research_tool = WebResearchTool()

    def execute_tool(
        self,
        *,
        tool_definition: dict,
        params: dict,
    ) -> dict:
        tool_type = tool_definition.get("tool_type")

        if tool_type == "db_query":
            return self._execute_db_query_tool(
                tool_definition=tool_definition,
                params=params,
            )

        if tool_type == "web_search":
            return self._execute_web_search_tool(
                tool_definition=tool_definition,
                params=params,
            )

        return {
            "success": False,
            "message": f"unsupported dynamic tool type: {tool_type}",
        }

    def _execute_db_query_tool(
        self,
        *,
        tool_definition: dict,
        params: dict,
    ) -> dict:
        execution_config = tool_definition.get("execution_config_json", {}) or {}

        table_name = execution_config.get("table_name")
        allowed_columns = execution_config.get("allowed_columns", []) or []
        default_limit = int(execution_config.get("default_limit", 10) or 10)
        keyword_param = execution_config.get("keyword_param")
        exact_filters = execution_config.get("exact_filters", {}) or {}

        if not table_name:
            return {
                "success": False,
                "message": "dynamic db_query tool missing table_name",
            }

        table = Table(table_name, self.metadata, autoload_with=self.db.bind)

        stmt = select(table).limit(min(default_limit, 20))

        if keyword_param and params.get(keyword_param):
            keyword = str(params[keyword_param])
            search_columns = []
            for column_name in allowed_columns:
                if column_name in table.c:
                    search_columns.append(cast(table.c[column_name], String))

            if search_columns:
                stmt = stmt.where(
                    or_(*[column.ilike(f"%{keyword}%") for column in search_columns])
                )

        for param_name, column_name in exact_filters.items():
            value = params.get(param_name)
            if value is None:
                continue
            if column_name in table.c:
                stmt = stmt.where(table.c[column_name] == value)

        rows = self.db.execute(stmt).mappings().all()

        cleaned_rows = []
        for row in rows:
            row_dict = dict(row)
            if allowed_columns:
                row_dict = {
                    key: value
                    for key, value in row_dict.items()
                    if key in allowed_columns
                }
            cleaned_rows.append(row_dict)

        return {
            "success": True,
            "tool_name": tool_definition.get("tool_name"),
            "tool_type": tool_definition.get("tool_type"),
            "table_name": table_name,
            "params": params,
            "rows": cleaned_rows,
            "row_count": len(cleaned_rows),
        }

    def _execute_web_search_tool(
        self,
        *,
        tool_definition: dict,
        params: dict,
    ) -> dict:
        execution_config = tool_definition.get("execution_config_json", {}) or {}
        query_param = execution_config.get("query_param", "keyword")
        max_results = int(execution_config.get("max_results", 5) or 5)

        query = params.get(query_param)
        if not query:
            return {
                "success": False,
                "message": f"dynamic web_search tool missing query param: {query_param}",
            }

        result = self.web_research_tool.run(
            query=str(query),
            max_results=max_results,
        )

        if not result.get("success"):
            return result

        return {
            "success": True,
            "tool_name": tool_definition.get("tool_name"),
            "tool_type": tool_definition.get("tool_type"),
            "params": params,
            "results": result.get("results", []),
            "row_count": len(result.get("results", [])),
        }