"""name_list_language_scope

Revision ID: 8c41c0a1f1a7
Revises: 7b1f2c0a2e91
Create Date: 2026-02-05 13:10:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = "8c41c0a1f1a7"
down_revision = "7b1f2c0a2e91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "name_list",
        sa.Column("language_scope", sa.String(length=20), nullable=False, server_default="ALL"),
    )
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE name_list
            SET language_scope='SPECIFIC'
            WHERE language IS NOT NULL AND language != '' AND language != 'all'
            """
        )
    )
    conn.execute(
        text(
            """
            UPDATE name_list
            SET language_scope='ALL'
            WHERE language_scope IS NULL OR language_scope=''
            """
        )
    )
    op.alter_column("name_list", "language_scope", server_default=None)

    op.create_table(
        "name_list_language",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("list_no", sa.String(length=100), nullable=False),
        sa.Column("language_code", sa.String(length=50), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=True),
        sa.Column("delete_time", sa.DateTime(), nullable=True),
        sa.Column("create_by", sa.String(length=50), nullable=True),
        sa.Column("update_by", sa.String(length=50), nullable=True),
        sa.Column("delete_by", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_name_list_language_list_no", "name_list_language", ["list_no"], unique=False)
    op.create_index("ix_name_list_language_language_code", "name_list_language", ["language_code"], unique=False)

    conn.execute(
        text(
            """
            INSERT INTO name_list_language (list_no, language_code, create_time, update_time)
            SELECT no, language, create_time, update_time
            FROM name_list
            WHERE language_scope='SPECIFIC' AND language IS NOT NULL AND language != '' AND language != 'all'
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_name_list_language_language_code", table_name="name_list_language")
    op.drop_index("ix_name_list_language_list_no", table_name="name_list_language")
    op.drop_table("name_list_language")
    op.drop_column("name_list", "language_scope")
