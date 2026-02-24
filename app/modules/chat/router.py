from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import require_permission
from app.core.config import settings

router = APIRouter()


@router.post("/chat/query", response_model=schema.ChatQueryResponse)
async def query_chat(
    request: schema.ChatQueryRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("chat_access")),
):
    """
    Provides structured, domain-locked automobile intelligence.
    - Validates request via Governance Gates.
    - Performs RAG against knowledge DB when required.
    - Returns structured responses.
    Rate limited to 20 requests/minute per IP.
    """
    # Apply rate limiting if available
    if hasattr(http_request.app.state, "limiter"):
        limiter = http_request.app.state.limiter
        await limiter.check_request(http_request, settings.RATE_LIMIT_CHAT)

    request.tenant_id = tenant_id
    user_id = current_user.get("sub")
    return await service.process_chat_query(db, request, user_id)


@router.get("/chat/examples")
async def get_chat_examples():
    return {
        "example1": {
            "query": "My car is making a grinding noise when I brake.",
            "vehicle": {"make": "Maruti", "model": "Swift", "year": 2019, "fuel": "petrol"},
        },
        "example2": {
            "query": "What are the common causes of engine overheating?",
        },
    }