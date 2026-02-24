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
    
    # Use pgvector if available (PostgreSQL), else JSON (SQLite)
    if PGVECTOR_AVAILABLE:
        embedding = Column(Vector(768))
    else:
        embedding_json = Column(Text, nullable=True)
    
    source_url = Column(String, default="")
    chunk_index = Column(Integer, default=0)
