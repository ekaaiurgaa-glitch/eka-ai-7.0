"""Add refresh_tokens table

Revision ID: 0021_refresh_tokens
"""
from alembic import op
import sqlalchemy as sa


revision = '0021_refresh_tokens'
down_revision = '0020_tenant_user_rls'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'refresh_tokens',
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('token')
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])


def downgrade():
    op.drop_index('ix_refresh_tokens_expires_at')
    op.drop_index('ix_refresh_tokens_user_id')
    op.drop_table('refresh_tokens')
