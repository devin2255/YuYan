from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class ListAppChannel(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_no = Column(String(100), nullable=False, index=True)
    app_id = Column(String(100), nullable=True, index=True)
    channel_id = Column(Integer, nullable=True, index=True)
