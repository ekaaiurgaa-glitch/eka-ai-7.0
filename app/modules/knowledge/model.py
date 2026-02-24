from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base, TenantMixin, TimestampMixin

try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False


class KnowledgeChunk(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    # Support both pgvector (PostgreSQL) and JSON (SQLite) embeddings
    # pgvector is preferred for performance; JSON is fallback for SQLite/dev
    if PGVECTOR_AVAILABLE:
        embedding = Column(Vector(768))  # Native vector for similarity search
        embedding_json = Column(Text, nullable=True)  # Keep for migration/compatibility
    else:
        embedding = Column(Text, nullable=True)  # Placeholder when pgvector unavailable
        embedding_json = Column(Text, nullable=True)  # JSON embeddings for SQLite
    
    source_url = Column(String, default="")
    chunk_index = Column(Integer, default=0)
