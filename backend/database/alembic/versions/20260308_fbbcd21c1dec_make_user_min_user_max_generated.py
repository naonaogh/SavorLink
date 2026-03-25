"""make user_min user_max generated

Revision ID: fbbcd21c1dec
Revises: 1c020ff9f495
Create Date: 2026-03-08 13:36:49.308140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "fbbcd21c1dec"
down_revision = "1c020ff9f495"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("chats", "user_min")
    op.drop_column("chats", "user_max")

    op.add_column(
        "chats",
        sa.Column(
            "user_min",
            sa.BigInteger(),
            sa.Computed("LEAST(user1_id, user2_id)", persisted=True),
        ),
    )

    op.add_column(
        "chats",
        sa.Column(
            "user_max",
            sa.BigInteger(),
            sa.Computed("GREATEST(user1_id, user2_id)", persisted=True),
        ),
    )

    op.create_index(
        "uq_chats_users",
        "chats",
        ["user_min", "user_max"],
        unique=True,
    )


def downgrade():
    op.drop_index("uq_chats_users", table_name="chats")

    op.drop_column("chats", "user_min")
    op.drop_column("chats", "user_max")

    op.add_column(
        "chats",
        sa.Column("user_min", sa.BigInteger(), nullable=False),
    )

    op.add_column(
        "chats",
        sa.Column("user_max", sa.BigInteger(), nullable=False),
    )