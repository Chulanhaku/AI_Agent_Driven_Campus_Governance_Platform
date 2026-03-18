"""add_policy_handbook_nodes_table

Revision ID: f8b2d4c9a1e0
Revises: 25b4f539c6d1
Create Date: 2026-03-17 11:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f8b2d4c9a1e0"
down_revision: Union[str, None] = "25b4f539c6d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "policy_handbook_nodes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("doc_name", sa.String(length=255), nullable=False),
        sa.Column("chapter", sa.String(length=255), nullable=True),
        sa.Column("section", sa.String(length=255), nullable=True),
        sa.Column("article_num", sa.String(length=64), nullable=True),
        sa.Column("article_title", sa.Text(), nullable=True),
        sa.Column("branded_content", sa.Text(), nullable=True),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("path", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_policy_handbook_nodes_doc_name"),
        "policy_handbook_nodes",
        ["doc_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policy_handbook_nodes_chapter"),
        "policy_handbook_nodes",
        ["chapter"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policy_handbook_nodes_article_num"),
        "policy_handbook_nodes",
        ["article_num"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_policy_handbook_nodes_article_num"), table_name="policy_handbook_nodes"
    )
    op.drop_index(
        op.f("ix_policy_handbook_nodes_chapter"), table_name="policy_handbook_nodes"
    )
    op.drop_index(
        op.f("ix_policy_handbook_nodes_doc_name"), table_name="policy_handbook_nodes"
    )
    op.drop_table("policy_handbook_nodes")
