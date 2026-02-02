from typing import Optional

from .common import APIModel


class CreateChannel(APIModel):
    no: str
    name: Optional[str] = None
    memo: Optional[str] = None
    username: str


class UpdateChannel(APIModel):
    name: str
    memo: Optional[str] = None
