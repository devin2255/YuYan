"""name_list_scope_and_list_app_channel

Revision ID: 7b1f2c0a2e91
Revises: 5af2e718ca64
Create Date: 2026-02-05 12:30:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = "7b1f2c0a2e91"
down_revision = "5af2e718ca64"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "name_list",
        sa.Column("scope", sa.String(length=20), nullable=False, server_default="APP_CHANNEL"),
    )
    conn = op.get_bind()
    conn.execute(text("UPDATE name_list SET scope='APP_CHANNEL' WHERE scope IS NULL OR scope=''"))
    op.alter_column("name_list", "scope", server_default=None)

    op.create_table(
        "list_app_channel_new",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("list_no", sa.String(length=100), nullable=False),
        sa.Column("app_id", sa.String(length=100), nullable=True),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=True),
        sa.Column("delete_time", sa.DateTime(), nullable=True),
        sa.Column("create_by", sa.String(length=50), nullable=True),
        sa.Column("update_by", sa.String(length=50), nullable=True),
        sa.Column("delete_by", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_list_app_channel_list_no", "list_app_channel_new", ["list_no"], unique=False)
    op.create_index("ix_list_app_channel_app_id", "list_app_channel_new", ["app_id"], unique=False)
    op.create_index("ix_list_app_channel_channel_id", "list_app_channel_new", ["channel_id"], unique=False)

    conn.execute(
        text(
            """
            INSERT INTO list_app_channel_new (
                list_no, app_id, channel_id, create_time, update_time, delete_time, create_by, update_by, delete_by
            )
            SELECT
                list_no, app_id, channel_id, create_time, update_time, delete_time, create_by, update_by, delete_by
            FROM list_app_channel
            """
        )
    )
    op.drop_table("list_app_channel")
    op.rename_table("list_app_channel_new", "list_app_channel")


def downgrade() -> None:
    op.create_table(
        "list_app_channel_old",
        sa.Column("list_no", sa.String(length=100), nullable=False),
        sa.Column("app_id", sa.String(length=100), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=True),
        sa.Column("delete_time", sa.DateTime(), nullable=True),
        sa.Column("create_by", sa.String(length=50), nullable=True),
        sa.Column("update_by", sa.String(length=50), nullable=True),
        sa.Column("delete_by", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("list_no", "app_id", "channel_id"),
    )
    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO list_app_channel_old (
                list_no, app_id, channel_id, create_time, update_time, delete_time, create_by, update_by, delete_by
            )
            SELECT
                list_no, app_id, channel_id, create_time, update_time, delete_time, create_by, update_by, delete_by
            FROM list_app_channel
            WHERE app_id IS NOT NULL AND channel_id IS NOT NULL
            """
        )
    )
    op.drop_table("list_app_channel")
    op.rename_table("list_app_channel_old", "list_app_channel")

    op.drop_column("name_list", "scope")
