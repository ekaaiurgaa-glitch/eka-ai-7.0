from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.base import Base, TenantMixin, TimestampMixin


class KnowledgeChunk(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    # embedding stored as JSON for SQLite compat; use pgvector Vector(768) for Postgres
    embedding_json = Column(Text, nullable=True)
    source_url = Column(String, default="")
    chunk_index = Column(Integer, default=0)
