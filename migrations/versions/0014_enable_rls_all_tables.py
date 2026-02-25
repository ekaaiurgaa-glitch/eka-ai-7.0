"""enable_rls_all_tables

Revision ID: 0014
Revises: 0013
Create Date: 2026-02-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None

def upgrade():
    # Only run on PostgreSQL
    connection = op.get_bind()
    if connection.dialect.name != 'postgresql':
        return

    # List of tables to apply RLS to
    tables = [
        'tenants', 'users', 'job_cards', 'vehicles', 'customers', 'invoices',
        'estimates', 'audit_logs', 'mg_contracts', 'mg_reserve_accounts',
        'mg_reserve_transactions', 'usage_aggregates', 'data_export_requests'
    ]

    for table in tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        if table == 'tenants':
            op.execute(f"""
                CREATE POLICY tenant_isolation_{table} ON {table}
                USING (id = current_setting('app.current_tenant', true)::uuid);
            """)
        else:
            op.execute(f"""
                CREATE POLICY tenant_isolation_{table} ON {table}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
            """)

def downgrade():
    connection = op.get_bind()
    if connection.dialect.name != 'postgresql':
        return

    tables = [
        'tenants', 'users', 'job_cards', 'vehicles', 'customers', 'invoices',
        'estimates', 'audit_logs', 'mg_contracts', 'mg_reserve_accounts',
        'mg_reserve_transactions', 'usage_aggregates', 'data_export_requests'
    ]

    for table in tables:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
