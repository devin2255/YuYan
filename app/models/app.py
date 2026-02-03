from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class App(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(100), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    access_key = Column(String(100))
