from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class Channel(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    memo = Column(String(100))
