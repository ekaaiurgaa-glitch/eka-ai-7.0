from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schema, service
from app.core.dependencies import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.post("/chat/query", response_model=schema.ChatQueryResponse)
async def query_chat(
    request: schema.ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Provides structured, domain-locked automobile intelligence.
    - Validates request via Governance Gates.
    - Performs RAG against knowledge DB (pgvector) when required (not implemented yet).
    - Returns structured responses.
    """
    user_id = current_user.get("sub")
    return await service.process_chat_query(db, request, user_id)

@router.get("/chat/examples")
async def get_chat_examples():
    # In a real app, these would be pulled from a database or a configuration file.
    return {
        "example1": {
            "query": "My car is making a grinding noise when I brake.",
            "vehicle": {"make": "Maruti", "model": "Swift", "year": 2019, "fuel": "petrol"}
        },
        "example2": {
            "query": "What are the common causes of engine overheating?",
        }
    }