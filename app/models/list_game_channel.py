from sqlalchemy import Column, String

from yuyan.app.models.base import BaseModel


class ListGameChannel(BaseModel):
    list_no = Column(String(100), primary_key=True)
    game_id = Column(String(100), primary_key=True)
    channel_no = Column(String(100), primary_key=True)
