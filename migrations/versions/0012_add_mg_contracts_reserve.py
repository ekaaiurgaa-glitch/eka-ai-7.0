"""add mg contracts and reserve tables

Revision ID: 0012
Revises: 0011
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa

revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade():
    # mg_formulas
    op.create_table('mg_formulas',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('make', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('fuel_type', sa.String(), nullable=False),
        sa.Column('annual_base_cost_inr', sa.Numeric(12, 2), nullable=False),
        sa.Column('parts_pct', sa.Numeric(5, 2), nullable=False, server_default='65.0'),
        sa.Column('labor_pct', sa.Numeric(5, 2), nullable=False, server_default='35.0'),
        sa.Column('valid_from', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("fuel_type IN ('petrol','diesel','cng','ev','hybrid')", name='fuel_type_check')
    )

    # city_indices
    op.create_table('city_indices',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('city', sa.String(), nullable=False, unique=True),
        sa.Column('tier', sa.String(), nullable=False),
        sa.Column('multiplier', sa.Numeric(4, 2), nullable=False),
        sa.CheckConstraint("tier IN ('tier1','tier2','tier3')", name='tier_check')
    )

    # mg_contracts
    op.create_table('mg_contracts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('vehicle_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('monthly_fee_inr', sa.Numeric(10, 2), nullable=False),
        sa.Column('risk_buffer_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('annual_estimate_inr', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('termination_reason', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("risk_level IN ('low','medium','high')", name='risk_level_check'),
        sa.CheckConstraint("status IN ('active','suspended','terminated','completed')", name='status_check')
    )

    # mg_reserve_accounts
    op.create_table('mg_reserve_accounts',
        sa.Column('tenant_id', sa.String(), primary_key=True),
        sa.Column('total_reserve_balance', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # mg_reserve_transactions
    op.create_table('mg_reserve_transactions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('mg_contract_id', sa.String(), nullable=True),
        sa.Column('transaction_type', sa.String(), nullable=False),
        sa.Column('amount_inr', sa.Numeric(10, 2), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("transaction_type IN ('deposit','withdrawal')", name='transaction_type_check')
    )

    # mg_reconciliation_reports
    op.create_table('mg_reconciliation_reports',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('report_month', sa.Date(), nullable=False),
        sa.Column('total_mg_revenue', sa.Numeric(14, 2), nullable=False),
        sa.Column('total_actual_cost', sa.Numeric(14, 2), nullable=False),
        sa.Column('net_surplus_deficit', sa.Numeric(14, 2), nullable=False),
        sa.Column('reserve_balance_eom', sa.Numeric(14, 2), nullable=False),
        sa.Column('contracts_count', sa.Integer(), nullable=False),
        sa.Column('overrun_contracts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('report_pdf_url', sa.String(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade():
    op.drop_table('mg_reconciliation_reports')
    op.drop_table('mg_reserve_transactions')
    op.drop_table('mg_reserve_accounts')
    op.drop_table('mg_contracts')
    op.drop_table('city_indices')
    op.drop_table('mg_formulas')
