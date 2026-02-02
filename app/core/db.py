from __future__ import annotations

from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


def init_engine(database_uri: str) -> Tuple:
    connect_args = {}
    if database_uri.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(
        database_uri,
        pool_pre_ping=True,
        future=True,
        connect_args=connect_args,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    return engine, SessionLocal
