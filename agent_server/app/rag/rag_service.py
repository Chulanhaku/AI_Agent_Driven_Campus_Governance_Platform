from app.config.settings import get_settings
from app.llm.base import BaseLlmProvider
from app.llm.embeddings_provider import BaseEmbeddingsProvider
from app.rag.chunker import TextChunker
from app.rag.document_loader import DocumentLoader
from app.rag.knowledge_indexer import KnowledgeIndexer
from app.rag.retriever import Retriever
from app.rag.vector_store import InMemoryVectorStore


class RagService:
    def __init__(
        self,
        *,
        embeddings_provider: BaseEmbeddingsProvider,
    ) -> None:
        self.embeddings_provider = embeddings_provider
        self.settings = get_settings()
        self.retriever: Retriever | None = None

    def build_index(self) -> None:
        vector_store = InMemoryVectorStore(self.embeddings_provider)
        document_loader = DocumentLoader()
        chunker = TextChunker(
            chunk_size=self.settings.rag_chunk_size,
            chunk_overlap=self.settings.rag_chunk_overlap,
        )
        indexer = KnowledgeIndexer(
            document_loader=document_loader,
            chunker=chunker,
            vector_store=vector_store,
        )
        indexer.build_index(self.settings.knowledge_dir)
        self.retriever = Retriever(vector_store)

    def rebuild_index(self) -> None:
        self.build_index()

    def get_retriever(self) -> Retriever:
        if self.retriever is None:
            self.build_index()
        return self.retriever