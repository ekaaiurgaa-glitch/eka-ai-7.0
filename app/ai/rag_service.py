from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from app.modules.knowledge.service import similarity_search
from app.db.session import AsyncSessionLocal

@dataclass
class KnowledgeChunk:
    content: str
    source: str
    relevance_score: float

async def retrieve_context(query: str, vehicle_context: Dict[str, Any], top_k: int = 5) -> List[KnowledgeChunk]:
    """
    1. Embed query using text-embedding-001 (via similarity_search)
    2. Add vehicle context to query: f"{vehicle_context['make']} {vehicle_context['model']} {query}"
    3. pgvector similarity search (or fallback)
    4. Return KnowledgeChunk list
    """
    import logging
    logger = logging.getLogger(__name__)
    
    make = vehicle_context.get('make', '')
    model_name = vehicle_context.get('model', '')
    
    # Enrich query with vehicle context for better RAG hits
    context_query = f"{make} {model_name} {query}".strip()
    logger.info(f"Retrieving context for: {context_query}")
    
    tenant_id = vehicle_context.get('tenant_id', 'tenant_admin')

    try:
        async with AsyncSessionLocal() as db:
            db_chunks = await similarity_search(db, context_query, tenant_id, top_k=top_k)
            
            # Convert DB model to KnowledgeChunk dataclass
            return [
                KnowledgeChunk(
                    content=c.content,
                    source=c.source_url or "internal_kb",
                    relevance_score=1.0 # similarity_search currently doesn't return scores easily in the common interface
                ) for c in db_chunks
            ]
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return []
