from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class RiskType(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    no = Column(Integer, nullable=False, index=True)
    desc = Column(String(100), nullable=False)
    abbrev = Column(String(100))
