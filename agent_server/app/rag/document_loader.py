import json
from pathlib import Path


class DocumentLoader:
    def load_directory(self, directory: str) -> list[dict]:
        docs = []
        base_path = Path(directory)

        if not base_path.exists():
            return docs

        for file_path in base_path.glob("*.txt"):
            content = file_path.read_text(encoding="utf-8")
            docs.append(
                {
                    "source": str(file_path),
                    "filename": file_path.name,
                    "content": content,
                }
            )

        for file_path in base_path.glob("*.jsonl"):
            records: list[dict] = []
            with file_path.open(encoding="utf-8") as f:
                for index, raw_line in enumerate(f):
                    line = raw_line.strip()
                    if not line:
                        continue

                    row = json.loads(line)
                    doc_name = (row.get("doc_name") or "上海大学本科生学生手册").strip()
                    chapter = (row.get("chapter") or "").strip()
                    article_num = (row.get("article_num") or "").strip()
                    article_title = (row.get("article_title") or "").strip()
                    raw_content = (row.get("raw_content") or "").strip()

                    title = " ".join(
                        part for part in [article_num, article_title] if part
                    )
                    if chapter:
                        filename = f"{doc_name}-{chapter}.txt"
                    else:
                        filename = f"{doc_name}.txt"

                    metadata_lines = [f"文档：{doc_name}"]
                    if chapter:
                        metadata_lines.append(f"章节：{chapter}")
                    if article_num:
                        metadata_lines.append(f"条款：{article_num}")
                    if article_title:
                        metadata_lines.append(f"标题：{article_title}")

                    content_lines = metadata_lines
                    if title:
                        content_lines.append(f"原文标题：{title}")
                    content_lines.append(f"正文：{raw_content}")

                    records.append(
                        {
                            "source": row.get("path") or str(file_path),
                            "filename": filename,
                            "chunk_id": int(index),
                            "content": "\n".join(content_lines),
                            "doc_name": doc_name,
                            "chapter": chapter,
                            "article_num": article_num,
                            "article_title": article_title,
                        }
                    )

            if records:
                docs.append(
                    {
                        "source": str(file_path),
                        "filename": file_path.name,
                        "content": "",
                        "prebuilt_chunks": records,
                    }
                )

        return docs