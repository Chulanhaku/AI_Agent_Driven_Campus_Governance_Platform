from fastapi import APIRouter, Depends

from app.api.deps import get_rag_service
from app.rag.rag_service import RagService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/rag/rebuild")
def rebuild_rag_index(
    rag_service = Depends(get_rag_service),
) -> dict:
    rag_service.rebuild_index()
    return {
        "status": "ok",
        "message": "RAG index rebuilt successfully",
    }