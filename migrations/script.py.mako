"""Alembic script mako template.

This is a Mako template that is used to generate migration scripts.
"""
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'REVISION'
down_revision = 'DOWN_REVISION'
branch_labels = None
depends_on = None

def upgrade():
    ${upgrades}

def downgrade():
    ${downgrades}
