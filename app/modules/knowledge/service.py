import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from . import model

try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False


async def get_embedding(text_input: str) -> List[float]:
    """
    Get embedding vector for text using Gemini embedding model.
    Falls back to a zero vector if the API is unavailable.
    """
    try:
        from google import genai
        from app.core.config import settings
        import asyncio
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        result = await asyncio.to_thread(
            client.models.embed_content,
            model="gemini-embedding-001",
            contents=text_input,
        )
        return result.embeddings[0].values
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Embedding failed: {e}")
        return [0.0] * 768


def _chunk_text(text_input: str, chunk_size: int = 500) -> List[str]:
    """Simple sentence-boundary chunker."""
    sentences = text_input.replace("\n", " ").split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) > chunk_size and current:
            chunks.append(current.strip())
            current = sentence + ". "
        else:
            current += sentence + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text_input]


async def ingest_document(db: AsyncSession, title: str, content: str, tenant_id: str, source_url: str = "") -> int:
    """Chunk, embed, and store a knowledge document. Returns number of chunks created."""
    chunks = _chunk_text(content)
    for idx, chunk_text in enumerate(chunks):
        embedding = await get_embedding(chunk_text)
        
        if PGVECTOR_AVAILABLE:
            db_chunk = model.KnowledgeChunk(
                tenant_id=tenant_id,
                title=title,
                content=chunk_text,
                embedding=embedding,
                source_url=source_url,
                chunk_index=idx,
            )
        else:
            db_chunk = model.KnowledgeChunk(
                tenant_id=tenant_id,
                title=title,
                content=chunk_text,
                embedding_json=json.dumps(embedding),
                source_url=source_url,
                chunk_index=idx,
            )
        db.add(db_chunk)
    await db.commit()
    return len(chunks)


async def similarity_search(db: AsyncSession, query: str, tenant_id: str, top_k: int = 3) -> List[model.KnowledgeChunk]:
    """
    Find top_k most similar knowledge chunks.
    Uses pgvector native operator if available, else in-memory numpy.
    """
    query_embedding = await get_embedding(query)
    
    if PGVECTOR_AVAILABLE:
        # Use pgvector native cosine distance
        result = await db.execute(
            select(model.KnowledgeChunk)
            .filter(model.KnowledgeChunk.tenant_id == tenant_id)
            .order_by(model.KnowledgeChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return result.scalars().all()
    else:
        # Fallback to in-memory numpy
        import numpy as np
        query_vec = np.array(query_embedding)
        
        result = await db.execute(
            select(model.KnowledgeChunk).filter(model.KnowledgeChunk.tenant_id == tenant_id)
        )
        chunks = result.scalars().all()
        if not chunks:
            return []
        
        scored = []
        for chunk in chunks:
            emb = np.array(json.loads(chunk.embedding_json) if chunk.embedding_json else [0.0] * 768)
            norm = np.linalg.norm(query_vec) * np.linalg.norm(emb)
            similarity = float(np.dot(query_vec, emb) / norm) if norm > 0 else 0.0
            scored.append((similarity, chunk))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
