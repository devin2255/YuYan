from typing import Any

from .common import APIModel


class ImageRequest(APIModel):
    accessKey: str
    data: Any
