from typing import Optional

from .common import APIModel


class CreateGame(APIModel):
    game_id: str
    name: str = ""
    username: str
    dun_secret_id: Optional[str] = None
    dun_secret_key: Optional[str] = None


class UpdateGame(APIModel):
    name: str
    username: str
    dun_secret_id: Optional[str] = None
    dun_secret_key: Optional[str] = None
