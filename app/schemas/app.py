from typing import Optional

from .common import APIModel


class CreateApp(APIModel):
    app_id: str
    name: str = ""
    username: str


class UpdateApp(APIModel):
    name: str
    username: str
