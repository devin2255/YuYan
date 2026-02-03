from .common import APIModel


class CreateAISwitch(APIModel):
    switch: str
    app_id: str
    username: str


class UpdateAISwitch(APIModel):
    switch: str
    username: str


class CreateACSwitch(APIModel):
    switch: str
    app_id: str
    channel: str
    username: str


class UpdateACSwitch(APIModel):
    switch: str
    username: str


class CreateThreshold(APIModel):
    threshold: float
    app_id: str
    username: str


class UpdateThreshold(APIModel):
    threshold: float
    username: str
