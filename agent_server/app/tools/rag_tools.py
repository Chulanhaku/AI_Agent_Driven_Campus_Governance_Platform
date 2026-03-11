from app.rag.retriever import Retriever
from app.tools.base import BaseTool


class QueryPolicyKnowledgeTool(BaseTool):
    name = "query_policy_knowledge"
    description = "查询校务制度与规则文档"

    def __init__(self, retriever: Retriever, top_k: int = 3) -> None:
        self.retriever = retriever
        self.top_k = top_k

    def run(self, *, question: str, **kwargs) -> dict:
        items = self.retriever.retrieve(query=question, top_k=self.top_k)

        result_items = []
        for item in items:
            result_items.append(
                {
                    "source": item["source"],
                    "filename": item["filename"],
                    "chunk_id": item["chunk_id"],
                    "content": item["content"],
                    "score": item["score"],
                }
            )

        return {
            "success": True,
            "tool_name": self.name,
            "items": result_items,
            "total": len(result_items),
        }