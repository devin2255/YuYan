from sqlalchemy import Column, Integer, String

from yuyan.app.models.base import BaseModel


class Language(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    abbrev = Column(String(50), nullable=False, index=True)
