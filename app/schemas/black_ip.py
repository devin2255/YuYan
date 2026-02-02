from typing import Optional

from .common import APIModel


class BlackIP(APIModel):
    ip: str
    username: Optional[str] = ""
