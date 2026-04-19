"""add user token version

Revision ID: 20260418_2b2a8d74f1b1
Revises: 89b18b3ad956
Create Date: 2026-04-18 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260418_2b2a8d74f1b1"
down_revision = "89b18b3ad956"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.alter_column("users", "token_version", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "token_version")
