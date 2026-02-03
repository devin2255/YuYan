from sqlalchemy import Column, Integer, String, Boolean

from app.models.base import BaseModel


class AISwitch(BaseModel):
    __tablename__ = "ai_switch"

    id = Column(Integer, primary_key=True, autoincrement=True)
    switch = Column(Boolean, nullable=False, default=True)
    app_id = Column(String(100), nullable=False, index=True)
