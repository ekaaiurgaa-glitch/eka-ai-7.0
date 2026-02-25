"""audit_log_immutability

Revision ID: 0015
Revises: 0014
Create Date: 2026-02-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None

def upgrade():
    # Enforce immutability on audit_logs using PostgreSQL rules
    # This matches the TDD Section 3.4
    op.execute("""
        CREATE OR REPLACE RULE no_update_audit_logs AS
        ON UPDATE TO audit_logs DO INSTEAD NOTHING;
    """)
    op.execute("""
        CREATE OR REPLACE RULE no_delete_audit_logs AS
        ON DELETE TO audit_logs DO INSTEAD NOTHING;
    """)

def downgrade():
    op.execute("DROP RULE IF EXISTS no_update_audit_logs ON audit_logs;")
    op.execute("DROP RULE IF EXISTS no_delete_audit_logs ON audit_logs;")
