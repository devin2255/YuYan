from typing import Optional

from .common import APIModel


class CreateRiskType(APIModel):
    no: int
    desc: str
    abbrev: Optional[str] = ""
    username: Optional[str] = ""
