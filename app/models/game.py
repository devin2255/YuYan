from sqlalchemy import Column, Integer, String

from yuyan.app.models.base import BaseModel


class Game(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(100), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    access_key = Column(String(100))
    dun_secret_id = Column(String(200))
    dun_secret_key = Column(String(200))
