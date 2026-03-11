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

        return docs