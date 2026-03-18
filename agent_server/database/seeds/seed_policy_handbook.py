import argparse
import json
import os
import sqlite3
from pathlib import Path

from sqlalchemy import text

from app.db.session import SessionLocal


INSERT_SQL = text(
    """
    INSERT INTO policy_handbook_nodes (
        doc_name,
        chapter,
        section,
        article_num,
        article_title,
        branded_content,
        raw_content,
        path
    ) VALUES (
        :doc_name,
        :chapter,
        :section,
        :article_num,
        :article_title,
        :branded_content,
        :raw_content,
        :path
    )
    """
)

DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent / "data" / "handbook.db"
DEFAULT_JSONL_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "knowledge"
    / "policy_handbook_nodes.jsonl"
)


def _load_from_sqlite(sqlite_path: str) -> list[dict]:
    conn = sqlite3.connect(sqlite_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                doc_name,
                chapter,
                section,
                article_num,
                article_title,
                branded_content,
                raw_content,
                path
            FROM handbook_nodes
            ORDER BY id
            """
        )
        rows = cursor.fetchall()

        records: list[dict] = []
        for row in rows:
            records.append(
                {
                    "doc_name": row[0] or "上海大学本科生学生手册",
                    "chapter": row[1],
                    "section": row[2],
                    "article_num": row[3],
                    "article_title": row[4],
                    "branded_content": row[5],
                    "raw_content": row[6] or "",
                    "path": row[7],
                }
            )

        return records
    finally:
        conn.close()


def _load_from_jsonl(jsonl_path: str) -> list[dict]:
    records: list[dict] = []
    with open(jsonl_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            row = json.loads(line)
            records.append(
                {
                    "doc_name": row.get("doc_name") or "上海大学本科生学生手册",
                    "chapter": row.get("chapter"),
                    "section": row.get("section"),
                    "article_num": row.get("article_num"),
                    "article_title": row.get("article_title"),
                    "branded_content": row.get("branded_content"),
                    "raw_content": row.get("raw_content") or "",
                    "path": row.get("path"),
                }
            )
    return records


def seed_policy_handbook(
    *,
    jsonl_path: str,
    sqlite_path: str,
    replace: bool = False,
) -> None:
    records: list[dict]
    if os.path.exists(jsonl_path):
        records = _load_from_jsonl(jsonl_path)
    elif os.path.exists(sqlite_path):
        records = _load_from_sqlite(sqlite_path)
    else:
        raise FileNotFoundError(
            "no source file found: provide --jsonl-path or --sqlite-path"
        )

    if not records:
        raise RuntimeError("no handbook records loaded from source")

    db = SessionLocal()
    try:
        existing_count = db.execute(
            text("SELECT COUNT(*) FROM policy_handbook_nodes")
        ).scalar_one()

        if existing_count > 0 and not replace:
            print(
                "policy_handbook_nodes already has data. Use --replace to reload data."
            )
            return

        if existing_count > 0 and replace:
            db.execute(text("TRUNCATE TABLE policy_handbook_nodes RESTART IDENTITY"))

        db.execute(INSERT_SQL, records)
        db.commit()
        print(f"seed policy handbook success: {len(records)} rows")
    except Exception as exc:
        db.rollback()
        print(f"seed policy handbook failed: {exc}")
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed SHU handbook nodes into PostgreSQL"
    )
    parser.add_argument(
        "--jsonl-path",
        default=os.getenv("POLICY_HANDBOOK_JSONL_PATH") or str(DEFAULT_JSONL_PATH),
        help="Path to handbook JSONL file",
    )
    parser.add_argument(
        "--sqlite-path",
        default=os.getenv("MYRAG_SQLITE_PATH") or str(DEFAULT_SQLITE_PATH),
        help="Path to fallback handbook.db sqlite file",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing data in policy_handbook_nodes",
    )
    args = parser.parse_args()

    seed_policy_handbook(
        jsonl_path=args.jsonl_path,
        sqlite_path=args.sqlite_path,
        replace=args.replace,
    )


if __name__ == "__main__":
    main()
