from typing import List, Optional, Union

from .common import APIModel


class CreateOrUpdateNameList(APIModel):
    name: str
    type: int
    match_rule: int
    match_type: int
    suggest: int
    risk_type: int
    status: Optional[int] = 1
    language: Optional[str] = "all"
    channel: Union[List[int], int]
    app_id: Union[List[str], str]
    username: str


class SwitchNameList(APIModel):
    status: int
    username: str
