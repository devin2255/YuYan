from typing import Any

from .common import APIModel


class ImageRequest(APIModel):
    access_key: str
    data: Any
