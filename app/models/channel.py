from sqlalchemy import Column, Integer, String

from yuyan.app.models.base import BaseModel


class Channel(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    no = Column(String(100), nullable=False, index=True)
    name = Column(String(100))
    memo = Column(String(100))
