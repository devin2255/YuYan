from typing import Optional

from .common import APIModel


class CreateChannel(APIModel):
    name: Optional[str] = None
    memo: Optional[str] = None
    username: str


class UpdateChannel(APIModel):
    name: str
    memo: Optional[str] = None
