from typing import Any

from .common import APIModel


class TextRequest(APIModel):
    access_key: str
    ugc_source: str
    data: Any
