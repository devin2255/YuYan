from sqlalchemy import Column, Integer, String

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    identity = Column(String(120), unique=True, index=True, nullable=False)
    display_name = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=False)
    roles = Column(String(200), default="admin")
    status = Column(Integer, default=1)

    def role_list(self):
        if not self.roles:
            return []
        return [item.strip() for item in self.roles.split(",") if item.strip()]
