"""add gdpr export and approval tables

Revision ID: 0013
Revises: 0012
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


def upgrade():
    # data_export_requests
    op.create_table('data_export_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('export_type', sa.String(), nullable=False),
        sa.Column('date_range_start', sa.Date(), nullable=True),
        sa.Column('date_range_end', sa.Date(), nullable=True),
        sa.Column('format', sa.String(), nullable=False, server_default='csv'),
        sa.Column('status', sa.String(), nullable=False, server_default='queued'),
        sa.Column('s3_url', sa.String(), nullable=True),
        sa.Column('s3_url_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.CheckConstraint("export_type IN ('job_cards','invoices','customers','audit_logs','full')", name='export_type_check'),
        sa.CheckConstraint("format IN ('csv','json','pdf')", name='format_check'),
        sa.CheckConstraint("status IN ('queued','processing','ready','failed','expired')", name='status_check')
    )

    # customer_approvals
    op.create_table('customer_approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_card_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('estimate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approval_token', sa.String(), nullable=False, unique=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.String(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('e_signature_ref', sa.String(), nullable=True),
        sa.Column('notification_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['job_card_id'], ['jobcard.id']),
        sa.CheckConstraint("status IN ('pending','approved','rejected','expired')", name='status_check')
    )

    # pdi_records
    op.create_table('pdi_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_card_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('checklist', postgresql.JSONB(), nullable=False),
        sa.Column('overall_passed', sa.Boolean(), nullable=False),
        sa.Column('inspector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('photos', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('inspected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['job_card_id'], ['jobcard.id'])
    )


def downgrade():
    op.drop_table('pdi_records')
    op.drop_table('customer_approvals')
    op.drop_table('data_export_requests')
