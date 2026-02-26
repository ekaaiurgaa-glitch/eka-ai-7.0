"""Add tenant and user tables with RLS

Revision ID: 0020_tenant_user_rls
Revises: 
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa


revision = '0020_tenant_user_rls'
down_revision = '0018'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('subscription_plan', sa.Enum('free', 'basic', 'pro', 'enterprise', name='subscriptionplan'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenants_tenant_id'), 'tenants', ['tenant_id'], unique=True)
    
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'manager', 'technician', 'viewer', name='userrole'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.tenant_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Enable RLS on existing tables
    op.execute("ALTER TABLE job_cards ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE invoices ENABLE ROW LEVEL SECURITY")
    
    # Create RLS policies
    op.execute("""
        CREATE POLICY tenant_isolation_job_cards ON job_cards
        USING (tenant_id = current_setting('app.current_tenant_id', TRUE))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_vehicles ON vehicles
        USING (tenant_id = current_setting('app.current_tenant_id', TRUE))
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_invoices ON invoices
        USING (tenant_id = current_setting('app.current_tenant_id', TRUE))
    """)


def downgrade():
    op.execute("DROP POLICY IF EXISTS tenant_isolation_invoices ON invoices")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_vehicles ON vehicles")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_job_cards ON job_cards")
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_tenants_tenant_id'), table_name='tenants')
    op.drop_table('tenants')
    
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='subscriptionplan').drop(op.get_bind(), checkfirst=False)
