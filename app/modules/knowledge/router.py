from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from . import service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import require_permission

router = APIRouter()


class IngestRequest(BaseModel):
    title: str
    content: str
    source_url: Optional[str] = ""


class IngestResponse(BaseModel):
    chunks_created: int
    title: str


class SearchResult(BaseModel):
    title: str
    content: str
    source_url: str
    chunk_index: int


@router.post("/knowledge/ingest", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_catalog")),
):
    """Admin endpoint: ingest a knowledge document into the RAG store."""
    n = await service.ingest_document(db, request.title, request.content, tenant_id, request.source_url)
    return IngestResponse(chunks_created=n, title=request.title)


@router.get("/knowledge/search", response_model=List[SearchResult])
async def search_knowledge(
    q: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_catalog")),
):
    """Debug endpoint: similarity search over the knowledge base."""
    chunks = await service.similarity_search(db, q, tenant_id)
    return [
        SearchResult(
            title=c.title,
            content=c.content,
            source_url=c.source_url or "",
            chunk_index=c.chunk_index,
        )
        for c in chunks
    ]
