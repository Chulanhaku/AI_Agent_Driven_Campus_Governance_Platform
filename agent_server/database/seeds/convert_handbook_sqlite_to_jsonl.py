import argparse
import json
import sqlite3
from pathlib import Path


DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent / "data" / "handbook.db"
DEFAULT_JSONL_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "knowledge"
    / "policy_handbook_nodes.jsonl"
)


def convert(sqlite_path: Path, jsonl_path: Path) -> int:
    if not sqlite_path.exists():
        raise FileNotFoundError(f"sqlite file not found: {sqlite_path}")

    conn = sqlite3.connect(str(sqlite_path))
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
    finally:
        conn.close()

    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            record = {
                "doc_name": row[0] or "上海大学本科生学生手册",
                "chapter": row[1],
                "section": row[2],
                "article_num": row[3],
                "article_title": row[4],
                "branded_content": row[5],
                "raw_content": row[6] or "",
                "path": row[7],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert handbook sqlite data to JSONL"
    )
    parser.add_argument(
        "--sqlite-path",
        default=str(DEFAULT_SQLITE_PATH),
        help="Path to source handbook.db sqlite file",
    )
    parser.add_argument(
        "--jsonl-path",
        default=str(DEFAULT_JSONL_PATH),
        help="Path to output JSONL file",
    )
    args = parser.parse_args()

    count = convert(Path(args.sqlite_path), Path(args.jsonl_path))
    print(f"convert handbook sqlite->jsonl success: {count} rows")


if __name__ == "__main__":
    main()
