"""add usage metering tables

Revision ID: 0011
Revises: 0010
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    # usage_events (partitioned by month)
    op.execute("""
        CREATE TABLE usage_events (
            id UUID DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            user_id UUID,
            event_type TEXT NOT NULL CHECK (event_type IN ('chat_query','operator_action','job_card_create','mg_calculation','dashboard_load','data_export')),
            tokens_consumed INT NOT NULL DEFAULT 0,
            storage_bytes BIGINT NOT NULL DEFAULT 0,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT now()
        ) PARTITION BY RANGE (created_at)
    """)
    
    # Create first partition
    op.execute("""
        CREATE TABLE usage_events_2026_01 PARTITION OF usage_events
        FOR VALUES FROM ('2026-01-01') TO ('2026-02-01')
    """)
    
    op.execute("""
        CREATE TABLE usage_events_2026_02 PARTITION OF usage_events
        FOR VALUES FROM ('2026-02-01') TO ('2026-03-01')
    """)

    # usage_aggregates
    op.create_table('usage_aggregates',
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('billing_cycle_start', sa.Date(), nullable=False),
        sa.Column('total_tokens_consumed', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('total_operator_actions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_job_cards_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_mg_calculations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_storage_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('total_api_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('tenant_id', 'billing_cycle_start')
    )

    # overage_ledger
    op.create_table('overage_ledger',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('billing_cycle', sa.Date(), nullable=False),
        sa.Column('overage_type', sa.String(), nullable=False),
        sa.Column('overage_units', sa.BigInteger(), nullable=False),
        sa.Column('rate_per_unit', sa.Numeric(10, 6), nullable=False),
        sa.Column('amount_inr', sa.Numeric(10, 2), nullable=False),
        sa.Column('billed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'])
    )


def downgrade():
    op.drop_table('overage_ledger')
    op.drop_table('usage_aggregates')
    op.execute('DROP TABLE usage_events')
