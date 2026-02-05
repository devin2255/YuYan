from typing import List, Optional

from .common import APIModel


class CreateOrUpdateNameList(APIModel):
    name: str
    type: int
    match_rule: int
    match_type: int
    suggest: int
    risk_type: int
    status: Optional[int] = 1
    language_scope: str
    language_codes: Optional[List[str]] = None
    scope: str
    app_ids: Optional[List[str]] = None
    channel_ids: Optional[List[int]] = None
    username: str


class SwitchNameList(APIModel):
    status: int
    username: str
