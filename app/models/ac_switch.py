from sqlalchemy import Column, Integer, String, Boolean

from app.models.base import BaseModel


class ACSwitch(BaseModel):
    __tablename__ = "ac_switch"

    id = Column(Integer, primary_key=True, autoincrement=True)
    switch = Column(Boolean, nullable=False, default=True)
    app_id = Column(String(100), nullable=False, index=True)
    channel = Column(String(100), nullable=False, index=True)
