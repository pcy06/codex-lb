"""enable sticky threads for untouched default dashboard settings

Revision ID: 20260401_000000_enable_sticky_threads_default
Revises: 20260330_000000_add_cache_locality_settings
Create Date: 2026-04-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision = "20260401_000000_enable_sticky_threads_default"
down_revision = "20260330_000000_add_cache_locality_settings"
branch_labels = None
depends_on = None


def _columns(connection: Connection, table_name: str) -> set[str]:
    inspector = sa.inspect(connection)
    if not inspector.has_table(table_name):
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    columns = _columns(bind, "dashboard_settings")
    if not {"id", "sticky_threads_enabled", "created_at", "updated_at"}.issubset(columns):
        return

    bind.execute(
        sa.text(
            """
            UPDATE dashboard_settings
            SET sticky_threads_enabled = 1
            WHERE id = 1
              AND sticky_threads_enabled = 0
              AND updated_at = created_at
            """
        )
    )


def downgrade() -> None:
    return
