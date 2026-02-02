from __future__ import annotations

import re
from datetime import datetime
from typing import Dict

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declared_attr

from yuyan.app.core.db import Base


def camel2line(camel: str) -> str:
    p = re.compile(r"([a-z]|\d)([A-Z])")
    line = re.sub(p, r"\1_\2", camel).lower()
    return line


class BaseModel(Base):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return camel2line(cls.__name__)

    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    delete_time = Column(DateTime, nullable=True)
    create_by = Column(String(50))
    update_by = Column(String(50))
    delete_by = Column(String(50))

    def to_dict(self) -> Dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def soft_delete(self, username: str = ""):
        self.delete_time = datetime.now()
        if username:
            self.delete_by = username
