"""add tenants users roles tables

Revision ID: 0017
Revises: 0016
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0017'
down_revision = '0016'
branch_labels = None
depends_on = None

def upgrade():
    # ── tenants table ──────────────────────────────────────────────
    op.create_table('tenants',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),  # workshop | fleet | individual
        sa.Column('plan_id', sa.String(), sa.ForeignKey('subscription_plans.id'), nullable=True),
        sa.Column('gst_number', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('tier', sa.String(), nullable=False, server_default='tier3'),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('deletion_scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # ── roles table ────────────────────────────────────────────────
    op.create_table('roles',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('permissions', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Seed default roles
    op.execute("""
        INSERT INTO roles (id, name, permissions, description) VALUES
        ('role_owner',      'owner',        '["chat_access","can_create_invoice","can_manage_jobs","can_manage_estimates","can_manage_vehicles","can_execute_operator","can_manage_catalog","can_manage_users","can_view_dashboard"]', 'Workshop owner — full access'),
        ('role_manager',    'manager',      '["chat_access","can_create_invoice","can_manage_jobs","can_manage_estimates","can_manage_vehicles","can_execute_operator","can_view_dashboard"]', 'Workshop manager'),
        ('role_technician', 'technician',   '["chat_access","can_manage_jobs"]', 'Service technician'),
        ('role_fleet_admin','fleet_admin',  '["chat_access","can_manage_vehicles","can_view_dashboard"]', 'Fleet administrator'),
        ('role_customer',   'customer',     '["can_view_dashboard"]', 'End customer — read-only dashboard');
    """)

    # ── users table ────────────────────────────────────────────────
    op.create_table('users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('role_id', sa.String(), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # ── customers table ────────────────────────────────────────────
    op.create_table('customers',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('gst_number', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),  # For inter-state GST
        sa.Column('is_anonymized', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_customers_tenant_id', 'customers', ['tenant_id'])

    # ── Enable RLS on new tables ───────────────────────────────────
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        for table in ['users', 'customers']:
            op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"""
                CREATE POLICY tenant_isolation_{table} ON {table}
                USING (tenant_id = current_setting('app.tenant_id', true));
            """)

def downgrade():
    op.drop_table('customers')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('tenants')
