"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-08-23 12:34:37.630365

"""

from typing import Sequence, Union

from alembic import op

from common.alembic.utils import read_sql_file

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    sql = read_sql_file("001_initial_schema.sql")
    op.execute(sql)
    
def downgrade():
    # Drop dependent tables first (tables with foreign keys)
    op.execute("DROP TABLE IF EXISTS user_businesses")
    
    # Drop triggers first before dropping tables
    op.execute("DROP TRIGGER IF EXISTS update_user_businesses_updated_at ON user_businesses")
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")
    op.execute("DROP TRIGGER IF EXISTS update_businesses_updated_at ON businesses")
    
    # Drop the function used by triggers
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Now drop the main tables
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TABLE IF EXISTS businesses")