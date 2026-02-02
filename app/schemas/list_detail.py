from typing import List, Optional, Union

from .common import APIModel


class CreateDetail(APIModel):
    list_no: str
    text: str
    username: str
    memo: Optional[str] = ""


class UpdateDetail(APIModel):
    text: str
    username: str
    memo: Optional[str] = ""


class CreateBatchDetail(APIModel):
    list_no: str
    data: Union[List[str], str]
    username: str


class DeleteDetailByText(APIModel):
    list_name: str
    text: str
    username: str


class DeleteDetail(APIModel):
    username: str


class DeleteBatchDetail(APIModel):
    ids: Union[List[int], str]
    username: str
