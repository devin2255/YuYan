from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class NameListLanguage(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_no = Column(String(100), nullable=False, index=True)
    language_code = Column(String(50), nullable=False, index=True)
