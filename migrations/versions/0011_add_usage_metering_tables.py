"""add usage metering tables

Revision ID: 0011
Revises: 0010
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa

revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    # usage_events (simplified - no partitioning for cross-dialect compatibility)
    op.create_table('usage_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('tokens_consumed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('storage_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # usage_aggregates
    op.create_table('usage_aggregates',
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('billing_cycle_start', sa.Date(), nullable=False),
        sa.Column('total_tokens_consumed', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('total_operator_actions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_job_cards_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_mg_calculations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_storage_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('total_api_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('tenant_id', 'billing_cycle_start')
    )

    # overage_ledger
    op.create_table('overage_ledger',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('billing_cycle', sa.Date(), nullable=False),
        sa.Column('overage_type', sa.String(), nullable=False),
        sa.Column('overage_units', sa.BigInteger(), nullable=False),
        sa.Column('rate_per_unit', sa.Numeric(10, 6), nullable=False),
        sa.Column('amount_inr', sa.Numeric(10, 2), nullable=False),
        sa.Column('billed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade():
    op.drop_table('overage_ledger')
    op.drop_table('usage_aggregates')
    op.drop_table('usage_events')
