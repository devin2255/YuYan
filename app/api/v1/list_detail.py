import json
from typing import List

from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session

from app.api.deps import get_ctx, get_db, get_current_user
from app.schemas.list_detail import (
    CreateBatchDetail,
    CreateDetail,
    DeleteBatchDetail,
    DeleteDetail,
    DeleteDetailByText,
    UpdateDetail,
)
from app.services import list_detail_service, name_list_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/list-details", dependencies=[Depends(get_current_user)])


def normalize_text_list(value) -> List[str]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if value.startswith("["):
            try:
                return json.loads(value)
            except Exception:
                pass
        return [i for i in value.split("\n") if i]
    return []


def normalize_ids(value) -> List[int]:
    if isinstance(value, list):
        return [int(i) for i in value]
    if isinstance(value, str):
        if value.startswith("["):
            try:
                return [int(i) for i in json.loads(value)]
            except Exception:
                pass
        return [int(i) for i in value.split(",") if i]
    return []


@router.get("/search")
def search_by_text(text: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    details = list_detail_service.get_detail_by_text(db, text)
    return to_dict(details)


@router.get("")
def get_details(db: Session = Depends(get_db)):
    list_detail_service.get_all(db)
    return success_response(msg="ok")


@router.get("/{did}")
def get_detail(did: int, db: Session = Depends(get_db)):
    detail = list_detail_service.get_detail(db, did)
    return to_dict(detail)


@router.post("")
async def create_detail(payload: CreateDetail, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    name_list = name_list_service.get_name_list_by_no(db, form.list_no.data)
    list_detail_service.add_detail(db, ctx, name_list, form)
    return success_response(msg="新增文本成功")


@router.post("/batch")
async def create_batch_detail(payload: CreateBatchDetail, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    data_list = normalize_text_list(form_data.data)
    form = FormProxy(list_no=form_data.list_no, data=data_list, username=form_data.username)
    name_list = name_list_service.get_name_list_by_no(db, form.list_no.data)
    list_detail_service.add_batch_detail(db, ctx, name_list, form)
    return success_response(msg="新增文本成功")


@router.put("/{did}")
async def update_detail(did: int, payload: UpdateDetail, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    detail = list_detail_service.get_detail(db, did)
    name_list = name_list_service.get_name_list(db, detail.list_id)
    list_detail_service.update_detail(db, ctx, detail, name_list, form)
    return success_response(msg="修改文本成功")


@router.delete("/by-text")
async def delete_detail_by_text(
    payload: DeleteDetailByText, db: Session = Depends(get_db), ctx=Depends(get_ctx)
):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    name_list = name_list_service.get_name_list_by_name(db, form.list_name.data)
    list_detail_service.remove_detail_by_text(db, ctx, name_list, form.text.data)
    return success_response(msg="删除文本成功")


@router.delete("/batch")
async def delete_batch_detail(payload: DeleteBatchDetail, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    ids = normalize_ids(form_data.ids)
    form = FormProxy(ids=ids, username=form_data.username)
    detail = list_detail_service.validate_ids(db, form.ids.data)
    name_list = name_list_service.get_name_list(db, detail.list_id)
    list_detail_service.remove_batch_detail(db, ctx, name_list, form)
    return success_response(msg="删除文本成功")


@router.delete("/{did}")
async def delete_detail(did: int, payload: DeleteDetail, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    detail = list_detail_service.get_detail(db, did)
    name_list = name_list_service.get_name_list(db, detail.list_id)
    list_detail_service.remove_detail(db, ctx, detail, name_list, form)
    return success_response(msg="删除文本成功")
