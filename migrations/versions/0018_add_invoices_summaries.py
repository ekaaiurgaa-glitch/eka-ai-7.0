"""add invoices and summaries

Revision ID: 0018
Revises: 0017
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa

revision = '0018'
down_revision = '0017'
branch_labels = None
depends_on = None

def upgrade():
    # invoices
    op.create_table('invoices',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('job_cards.id')),
        sa.Column('lines', sa.JSON()),
        sa.Column('total_amount', sa.Float()),
        sa.Column('tax_amount', sa.Float()),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # job_summaries
    op.create_table('job_summaries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('job_cards.id'), unique=True, index=True),
        sa.Column('job_state_at_summary', sa.String()),
        sa.Column('technical_summary', sa.String()),
        sa.Column('customer_summary', sa.String()),
        sa.Column('urgency', sa.String()),
        sa.Column('estimated_cost', sa.Float()),
        sa.Column('recommended_action', sa.String()),
        sa.Column('generated_at', sa.DateTime()),
        sa.Column('force_refresh', sa.Boolean(), default=False),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # operator_previews
    op.create_table('operator_previews',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('actor_id', sa.String()),
        sa.Column('tool_name', sa.String()),
        sa.Column('args_json', sa.JSON()),
        sa.Column('preview_json', sa.JSON()),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # operator_executions
    op.create_table('operator_executions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('preview_id', sa.String(), sa.ForeignKey('operator_previews.id')),
        sa.Column('execution_result', sa.JSON()),
        sa.Column('status', sa.String()), # success, error
        sa.Column('tenant_id', sa.String(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

def downgrade():
    op.drop_table('operator_executions')
    op.drop_table('operator_previews')
    op.drop_table('job_summaries')
    op.drop_table('invoices')
