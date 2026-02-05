"""create auth user table

Revision ID: 9d2e0f2c1a0b
Revises: 8c41c0a1f1a7
Create Date: 2026-02-05 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d2e0f2c1a0b"
down_revision = "8c41c0a1f1a7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_user",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("identity", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("roles", sa.String(length=200), nullable=True),
        sa.Column("status", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=True),
        sa.Column("delete_time", sa.DateTime(), nullable=True),
        sa.Column("create_by", sa.String(length=50), nullable=True),
        sa.Column("update_by", sa.String(length=50), nullable=True),
        sa.Column("delete_by", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identity"),
    )
    op.create_index("ix_auth_user_identity", "auth_user", ["identity"], unique=False)


def downgrade():
    op.drop_index("ix_auth_user_identity", table_name="auth_user")
    op.drop_table("auth_user")
