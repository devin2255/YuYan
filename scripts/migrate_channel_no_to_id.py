from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text

from app.core.config import load_settings


def _column_exists(conn, table: str, column: str) -> bool:
    sql = """
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = :table
      AND COLUMN_NAME = :column
    LIMIT 1
    """
    return conn.execute(text(sql), {"table": table, "column": column}).first() is not None


def main() -> int:
    settings = load_settings()
    url = os.getenv("SQLALCHEMY_DATABASE_URI") or settings.SQLALCHEMY_DATABASE_URI
    engine = create_engine(url, pool_pre_ping=True)

    with engine.begin() as conn:
        has_channel_no = _column_exists(conn, "channel", "no")
        has_lac_channel_no = _column_exists(conn, "list_app_channel", "channel_no")
        has_lac_channel_id = _column_exists(conn, "list_app_channel", "channel_id")

        if not (has_channel_no and has_lac_channel_no and has_lac_channel_id):
            print(
                "迁移条件不满足：需要 channel.no、list_app_channel.channel_no、list_app_channel.channel_id 均存在。"
            )
            return 1

        conn.execute(
            text(
                """
                UPDATE list_app_channel lac
                JOIN channel c ON lac.channel_no = c.no
                SET lac.channel_id = c.id
                """
            )
        )

        unmatched = conn.execute(
            text("SELECT COUNT(*) FROM list_app_channel WHERE channel_id IS NULL")
        ).scalar()
        print(f"迁移完成，未匹配记录数: {unmatched}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
