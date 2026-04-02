from dataclasses import dataclass

from app.llm.base import BaseLlmProvider
from app.llm.embeddings_provider import BaseEmbeddingsProvider
from app.rag.rag_service import RagService
from app.self_iteration.capability_registry import CapabilityRegistry


@dataclass
class AppContainer:
    llm_provider: BaseLlmProvider
    embeddings_provider: BaseEmbeddingsProvider
    rag_service: RagService
    capability_registry: CapabilityRegistry