from typing import Any

from .common import APIModel


class TextRequest(APIModel):
    accessKey: str
    ugcSource: str
    data: Any
