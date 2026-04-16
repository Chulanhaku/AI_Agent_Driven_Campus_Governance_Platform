from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.self_iteration.research_rules import ResearchRules
from app.tools.base import BaseTool


class DbSchemaSearchTool(BaseTool):
    name = "db_schema_search"
    description = "查询数据库 schema 信息，仅返回 allowlist 表结构"

    def __init__(self, db: Session) -> None:
        self.db = db

    def run(
        self,
        *,
        keywords: list[str] | None = None,
        **kwargs,
    ) -> dict:
        inspector = inspect(self.db.bind)
        all_tables = inspector.get_table_names()
        allowlist_tables = set(ResearchRules.get_allowlist_tables())

        selected_tables = [table for table in all_tables if table in allowlist_tables]

        if keywords:
            lowered_keywords = [item.lower() for item in keywords]
            selected_tables = [
                table for table in selected_tables
                if any(keyword in table.lower() for keyword in lowered_keywords)
            ]

        results = []
        for table_name in selected_tables:
            columns = inspector.get_columns(table_name)
            pk = inspector.get_pk_constraint(table_name)
            fks = inspector.get_foreign_keys(table_name)

            results.append(
                {
                    "table_name": table_name,
                    "columns": [
                        {
                            "name": col.get("name"),
                            "type": str(col.get("type")),
                            "nullable": col.get("nullable"),
                        }
                        for col in columns
                    ],
                    "primary_key": pk.get("constrained_columns", []),
                    "foreign_keys": [
                        {
                            "constrained_columns": fk.get("constrained_columns", []),
                            "referred_table": fk.get("referred_table"),
                            "referred_columns": fk.get("referred_columns", []),
                        }
                        for fk in fks
                    ],
                }
            )

        return {
            "success": True,
            "results": results,
        }