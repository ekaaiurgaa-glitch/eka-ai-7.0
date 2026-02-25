"""core tables

Revision ID: 0009
Revises: 
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa

revision = '0009'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # vehicles
    op.create_table('vehicles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('plate_number', sa.String(), index=True),
        sa.Column('make', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('fuel_type', sa.String(), nullable=False), # SQLite compatible
        sa.Column('vin', sa.String(), unique=True, index=True, nullable=True),
        sa.Column('owner_name', sa.String(), nullable=True),
        sa.Column('monthly_km', sa.Integer(), default=1000),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # job_cards
    op.create_table('job_cards',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_no', sa.String(), unique=True, index=True),
        sa.Column('vehicle_id', sa.Integer(), sa.ForeignKey('vehicles.id'), index=True),
        sa.Column('complaint', sa.String()),
        sa.Column('state', sa.String(), default="OPEN"),
        sa.Column('created_by', sa.String()),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # estimates
    op.create_table('estimates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('job_cards.id')),
        sa.Column('lines', sa.JSON()),
        sa.Column('total_parts', sa.Float()),
        sa.Column('total_labor', sa.Float()),
        sa.Column('tax_breakdown', sa.JSON()),
        sa.Column('approved', sa.Boolean(), default=False),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # parts
    op.create_table('parts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('part_number', sa.String(), index=True, nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('hsn_code', sa.String(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('gst_rate', sa.Float(), default=18.0),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # labor_rates
    op.create_table('labor_rates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('service_type', sa.String(), nullable=False),
        sa.Column('city', sa.String(), default="default"),
        sa.Column('rate_per_hour', sa.Float(), nullable=False),
        sa.Column('estimated_hours', sa.Float(), default=1.0),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

def downgrade():
    op.drop_table('labor_rates')
    op.drop_table('parts')
    op.drop_table('estimates')
    op.drop_table('job_cards')
    op.drop_table('vehicles')
