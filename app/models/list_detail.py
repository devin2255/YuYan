from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class ListDetail(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, nullable=False)
    list_no = Column(String(100), index=True)
    text = Column(String(100), nullable=False)
    memo = Column(String(100))
