from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class KnowledgeChunk:
    content: str
    source: str
    relevance_score: float

async def retrieve_context(query: str, vehicle_context: Dict[str, Any], top_k: int = 5) -> List[KnowledgeChunk]:
    """
    1. Embed query using text-embedding-004 (Google)
    2. Add vehicle context to query: f"{vehicle_context['make']} {vehicle_context['model']} {query}"
    3. pgvector similarity search
    4. Filter by relevance score > 0.75
    5. Return KnowledgeChunk list
    """
    import logging
    logger = logging.getLogger(__name__)
    
    context_query = f"{vehicle_context.get('make', '')} {vehicle_context.get('model', '')} {query}".strip()
    logger.info(f"Retrieving context for: {context_query}")
    
    # Mock behavior to simulate pgvector lookup since we don't have the actual db connection here
    chunks = [
        KnowledgeChunk(
            content="Brake noise diagnosis for Maruti Swift: check pads and rotors.",
            source="maruti_manuals",
            relevance_score=0.95
        ),
        KnowledgeChunk(
            content="Swift standard brake pad replacement procedure is ~2 hours labor.",
            source="labor_manuals",
            relevance_score=0.88
        )
    ]
    
    return [c for c in chunks if c.relevance_score > 0.75][:top_k]
