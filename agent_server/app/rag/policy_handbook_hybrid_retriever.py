import logging
import re

from sqlalchemy import text

from app.db.session import SessionLocal


logger = logging.getLogger(__name__)


class PolicyHandbookHybridRetriever:
    def __init__(
        self,
        *,
        vector_retriever,
        sql_top_k: int = 3,
        vector_top_k: int = 3,
    ) -> None:
        self.vector_retriever = vector_retriever
        self.sql_top_k = max(1, sql_top_k)
        self.vector_top_k = max(1, vector_top_k)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        top_k = max(1, top_k)

        sql_items = self._retrieve_from_sql(query=query, limit=self.sql_top_k)
        vector_items = self.vector_retriever.retrieve(
            query=query,
            top_k=max(top_k, self.vector_top_k),
        )

        merged: list[dict] = []
        seen: set[str] = set()

        for item in sql_items + vector_items:
            key = self._dedupe_key(item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)

        merged.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        return merged[:top_k]

    def _retrieve_from_sql(self, *, query: str, limit: int) -> list[dict]:
        try:
            article_match = re.search(r"第[一二三四五六七八九十百千零两0-9]+条", query)
            chapter_match = re.search(r"第[一二三四五六七八九十百千零两0-9]+章", query)

            with SessionLocal() as db:
                if article_match:
                    rows = (
                        db.execute(
                            text(
                                """
                            SELECT id, doc_name, chapter, article_num, article_title, raw_content, path
                            FROM policy_handbook_nodes
                            WHERE article_num = :article_num
                            ORDER BY id
                            LIMIT :limit
                            """
                            ),
                            {
                                "article_num": article_match.group(0),
                                "limit": limit,
                            },
                        )
                        .mappings()
                        .all()
                    )
                    if rows:
                        return [self._map_row(row, score=1.0) for row in rows]

                if chapter_match:
                    rows = (
                        db.execute(
                            text(
                                """
                            SELECT id, doc_name, chapter, article_num, article_title, raw_content, path
                            FROM policy_handbook_nodes
                            WHERE chapter ILIKE :chapter
                            ORDER BY id
                            LIMIT :limit
                            """
                            ),
                            {
                                "chapter": f"%{chapter_match.group(0)}%",
                                "limit": limit,
                            },
                        )
                        .mappings()
                        .all()
                    )
                    if rows:
                        return [self._map_row(row, score=0.98) for row in rows]

                rows: list[dict] = []
                for keyword in self._extract_keywords(query):
                    remain = limit - len(rows)
                    if remain <= 0:
                        break

                    partial_rows = (
                        db.execute(
                            text(
                                """
                            SELECT id, doc_name, chapter, article_num, article_title, raw_content, path
                            FROM policy_handbook_nodes
                            WHERE raw_content ILIKE :keyword
                               OR article_title ILIKE :keyword
                               OR chapter ILIKE :keyword
                            ORDER BY id
                            LIMIT :limit
                            """
                            ),
                            {
                                "keyword": f"%{keyword}%",
                                "limit": remain,
                            },
                        )
                        .mappings()
                        .all()
                    )

                    for row in partial_rows:
                        if any(
                            existing.get("id") == row.get("id") for existing in rows
                        ):
                            continue
                        rows.append(row)
                        if len(rows) >= limit:
                            break

            return [self._map_row(row, score=0.92) for row in rows]
        except Exception as exc:
            logger.warning("policy handbook sql retrieval failed: %s", exc)
            return []

    def _map_row(self, row: dict, *, score: float) -> dict:
        article_num = (row.get("article_num") or "").strip()
        article_title = (row.get("article_title") or "").strip()
        raw_content = (row.get("raw_content") or "").strip()

        title_parts: list[str] = []
        if article_num:
            title_parts.append(article_num)
        if article_title and article_title != article_num:
            title_parts.append(article_title)
        title = " ".join(title_parts)
        content = f"{title}\n{raw_content}" if title else raw_content

        doc_name = row.get("doc_name") or "上海大学学生手册"
        chapter = (row.get("chapter") or "").strip()
        if chapter:
            filename = f"{doc_name}-{chapter}.txt"
        else:
            filename = f"{doc_name}.txt"

        return {
            "source": row.get("path") or "policy_handbook_nodes",
            "filename": filename,
            "chunk_id": int(row.get("id") or 0),
            "content": content,
            "score": score,
        }

    def _extract_keywords(self, query: str) -> list[str]:
        query = query.strip()
        if not query:
            return []

        known_keywords = [
            "请假",
            "学籍",
            "学位",
            "转专业",
            "补考",
            "重修",
            "违纪",
            "作弊",
            "处分",
            "奖学金",
            "助学金",
            "学分",
            "选课",
            "休学",
            "复学",
            "退学",
            "毕业",
            "考试",
            "缓考",
            "辅修",
            "社团",
        ]

        found = [kw for kw in known_keywords if kw in query]
        if found:
            return found

        return [query]

    def _dedupe_key(self, item: dict) -> str:
        filename = (item.get("filename") or "").strip().lower()
        content = (item.get("content") or "").strip().replace("\n", " ")
        normalized = " ".join(content.split())

        marker_match = re.search(
            r"第[一二三四五六七八九十百千零两0-9]+(条|章)", normalized
        )
        if marker_match:
            return f"{filename}:{marker_match.group(0)}"

        if normalized:
            return f"{filename}:{normalized[:220]}"

        source = (item.get("source") or "").strip().lower()
        chunk_id = item.get("chunk_id", "")
        return f"{filename}:{source}:{chunk_id}"
