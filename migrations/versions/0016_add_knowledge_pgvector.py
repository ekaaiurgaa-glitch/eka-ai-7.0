"""add knowledge pgvector table

Revision ID: 0016
Revises: 0015
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None

def upgrade():
    # knowledge_chunks table
    # Using sa.JSON or sa.PickleType for embedding if not on Postgres
    op.create_table('knowledge_chunks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True), 
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        # Enable pgvector extension and convert column
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        op.execute("ALTER TABLE knowledge_chunks ALTER COLUMN embedding TYPE vector(768) USING embedding::vector(768);")
        op.execute("CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);")

def downgrade():
    op.drop_table('knowledge_chunks')
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        op.execute("DROP EXTENSION IF EXISTS vector;")
