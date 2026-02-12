"""add_workflows_table

Revision ID: d4e5f6a7b8c9
Revises: c3a1b2c3d4e5
Create Date: 2026-02-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, server_default='Untitled Workflow'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('graph_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default='{"nodes":[],"connections":[]}'),
        sa.Column('node_configs', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default='{}'),
        sa.Column('status', sa.Enum('draft', 'ready', 'running', 'completed', 'failed',
                                     name='workflowstatus'), nullable=False, server_default='draft'),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default='{}'),
        sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('template_category', sa.String(length=100), nullable=True),
        sa.Column('canvas_state', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default='{"zoom":1,"panX":0,"panY":0}'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  server_default='[]'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_id'), 'workflows', ['id'], unique=False)
    op.create_index(op.f('ix_workflows_user_id'), 'workflows', ['user_id'], unique=False)
    op.create_index('ix_workflows_user_updated', 'workflows', ['user_id', 'updated_at'], unique=False)
    op.create_index('ix_workflows_user_status', 'workflows', ['user_id', 'status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_workflows_user_status', table_name='workflows')
    op.drop_index('ix_workflows_user_updated', table_name='workflows')
    op.drop_index(op.f('ix_workflows_user_id'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_id'), table_name='workflows')
    op.drop_table('workflows')
    op.execute("DROP TYPE IF EXISTS workflowstatus")
