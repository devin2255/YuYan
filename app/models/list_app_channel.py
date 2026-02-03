from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class ListAppChannel(BaseModel):
    list_no = Column(String(100), primary_key=True)
    app_id = Column(String(100), primary_key=True)
    channel_id = Column(Integer, primary_key=True)
