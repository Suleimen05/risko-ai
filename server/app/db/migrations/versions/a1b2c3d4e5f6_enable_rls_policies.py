"""enable_rls_policies

Revision ID: a1b2c3d4e5f6
Revises: fb2d43a15f44
Create Date: 2026-02-12 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fb2d43a15f44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All user-owned tables with user_id FK
USER_TABLES = [
    'user_settings',
    'trends',
    'user_favorites',
    'user_searches',
    'user_scripts',
    'chat_sessions',
    'chat_messages',
    'competitors',
    'user_accounts',
    'workflows',
    'workflow_runs',
]


def upgrade() -> None:
    # Enable RLS on all user-owned tables
    for table in USER_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            CREATE POLICY {table}_user_isolation ON {table}
            FOR ALL
            USING (user_id = current_setting('app.current_user_id', true)::integer)
            WITH CHECK (user_id = current_setting('app.current_user_id', true)::integer);
        """)

    # Users table: self-isolation
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY users_self_isolation ON users
        FOR ALL
        USING (id = current_setting('app.current_user_id', true)::integer)
        WITH CHECK (id = current_setting('app.current_user_id', true)::integer);
    """)


def downgrade() -> None:
    for table in USER_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_user_isolation ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    op.execute("DROP POLICY IF EXISTS users_self_isolation ON users;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
