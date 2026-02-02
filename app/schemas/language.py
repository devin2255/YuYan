from typing import Optional

from .common import APIModel


class CreateOrUpdateLanguage(APIModel):
    name: str
    abbrev: str
    username: Optional[str] = ""


class DeleteLanguage(APIModel):
    username: Optional[str] = ""
