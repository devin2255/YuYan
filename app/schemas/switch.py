from .common import APIModel


class CreateAISwitch(APIModel):
    switch: str
    game_id: str
    username: str


class UpdateAISwitch(APIModel):
    switch: str
    username: str


class CreateACSwitch(APIModel):
    switch: str
    game_id: str
    channel: str
    username: str


class UpdateACSwitch(APIModel):
    switch: str
    username: str


class CreateThreshold(APIModel):
    threshold: float
    game_id: str
    username: str


class UpdateThreshold(APIModel):
    threshold: float
    username: str
