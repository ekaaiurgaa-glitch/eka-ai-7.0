"""add subscription tables

Revision ID: 0010
Revises: 
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0010'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # subscription_plans (no tenant_id - global config)
    op.create_table('subscription_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('plan_name', sa.String(), nullable=False, unique=True),
        sa.Column('monthly_price_inr', sa.Numeric(10, 2), nullable=False),
        sa.Column('token_limit', sa.BigInteger(), nullable=True),
        sa.Column('operator_actions_per_day', sa.Integer(), nullable=True),
        sa.Column('job_card_limit_per_month', sa.Integer(), nullable=True),
        sa.Column('api_requests_per_minute', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('enforcement_policy', sa.String(), nullable=False),
        sa.Column('overage_rate_per_1k_tokens', sa.Numeric(8, 4), nullable=True),
        sa.Column('features', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.CheckConstraint("enforcement_policy IN ('hard_stop','soft_limit','overage_billing','grace_period')", name='enforcement_policy_check')
    )

    # tenant_subscriptions
    op.create_table('tenant_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('billing_cycle_start', sa.Date(), nullable=False),
        sa.Column('billing_cycle_end', sa.Date(), nullable=False),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('payment_method_ref', sa.String(), nullable=True),
        sa.Column('grace_period_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id']),
        sa.CheckConstraint("status IN ('active','expired','suspended','cancelled','grace_period')", name='status_check')
    )


def downgrade():
    op.drop_table('tenant_subscriptions')
    op.drop_table('subscription_plans')
