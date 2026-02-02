from sqlalchemy import Column, Integer, String, Float

from yuyan.app.models.base import BaseModel


class ModelThreshold(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(100), nullable=False, index=True)
    threshold = Column(Float, nullable=False)
