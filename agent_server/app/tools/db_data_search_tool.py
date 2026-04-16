from sqlalchemy import MetaData, Table, or_, select, cast, String
from sqlalchemy.orm import Session

from app.self_iteration.research_rules import ResearchRules
from app.tools.base import BaseTool


class DbDataSearchTool(BaseTool):
    name = "db_data_search"
    description = "在 allowlist 表中执行受控只读搜索"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.metadata = MetaData()

    def run(
        self,
        *,
        table_name: str,
        keyword: str,
        limit: int = 5,
        **kwargs,
    ) -> dict:
        if not ResearchRules.is_table_allowed(table_name):
            return {
                "success": False,
                "message": f"table not allowed: {table_name}",
            }

        table = Table(table_name, self.metadata, autoload_with=self.db.bind)

        searchable_columns = []
        for column in table.columns:
            try:
                if isinstance(column.type, String):
                    searchable_columns.append(column)
                else:
                    searchable_columns.append(cast(column, String))
            except Exception:
                continue

        if not searchable_columns:
            return {
                "success": True,
                "results": [],
                "message": "no searchable columns",
            }

        conditions = [col.ilike(f"%{keyword}%") for col in searchable_columns]
        stmt = select(table).where(or_(*conditions)).limit(min(limit, 10))

        rows = self.db.execute(stmt).mappings().all()

        return {
            "success": True,
            "table_name": table_name,
            "keyword": keyword,
            "results": [dict(row) for row in rows],
        }