from app.rag.chunker import TextChunker
from app.rag.document_loader import DocumentLoader
from app.rag.vector_store import InMemoryVectorStore


class KnowledgeIndexer:
    def __init__(
        self,
        document_loader: DocumentLoader,
        chunker: TextChunker,
        vector_store: InMemoryVectorStore,
    ) -> None:
        self.document_loader = document_loader
        self.chunker = chunker
        self.vector_store = vector_store

    def build_index(self, directory: str) -> None:
        docs = self.document_loader.load_directory(directory)

        chunk_items = []
        for doc in docs:
            prebuilt_chunks = doc.get("prebuilt_chunks") or []
            if prebuilt_chunks:
                chunk_items.extend(prebuilt_chunks)
                continue

            chunks = self.chunker.split_text(doc["content"])
            for idx, chunk in enumerate(chunks):
                chunk_items.append(
                    {
                        "source": doc["source"],
                        "filename": doc["filename"],
                        "chunk_id": idx,
                        "content": chunk,
                    }
                )

        self.vector_store.add_texts(chunk_items)