from sqlalchemy import Column, Integer, String, Float

from app.models.base import BaseModel


class ModelThreshold(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(100), nullable=False, index=True)
    threshold = Column(Float, nullable=False)
