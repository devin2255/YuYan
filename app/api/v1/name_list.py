import json
from typing import List

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_ctx, get_db
from app.schemas.name_list import CreateOrUpdateNameList, SwitchNameList
from app.services import channel_service, app_service, name_list_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/name-lists")


def normalize_list(value) -> List[str]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if value.startswith("["):
            try:
                return json.loads(value)
            except Exception:
                pass
        return [i for i in value.split(",") if i]
    return []


def process_app_channel(db: Session, app_id, channel):
    app_ids = normalize_list(app_id)
    channel_ids = normalize_list(channel)

    if len(app_ids) > 5 or len(channel_ids) > 5:
        return [], []

    if app_ids:
        apps = [app_service.get_app(db, gid) for gid in app_ids]
    else:
        apps = [app_service.get_app(db, app_id)]

    if channel_ids:
        channels = [channel_service.get_channel(db, int(cid)) for cid in channel_ids]
    else:
        channels = [channel_service.get_channel(db, int(channel))]
    return apps, channels


@router.get("/{lid}")
def get_name_list(lid: str, db: Session = Depends(get_db)):
    data = name_list_service.get_name_list_by_name(db, lid)
    return to_dict(data)


@router.get("")
def get_name_lists(db: Session = Depends(get_db)):
    data = name_list_service.get_name_lists(db)
    return to_dict(data)


@router.post("")
async def create_name_list(payload: CreateOrUpdateNameList, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    apps, channels = process_app_channel(db, form.app_id.data, form.channel.data)
    name_list_service.create_name_list(db, ctx, form, apps, channels)
    return success_response(msg="新建名单成功")


@router.put("/{lid}")
async def update_name_list(
    lid: str, payload: CreateOrUpdateNameList, db: Session = Depends(get_db), ctx=Depends(get_ctx)
):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    apps, channels = process_app_channel(db, form.app_id.data, form.channel.data)
    name_list_service.update_name_list(db, ctx, lid, form, apps, channels)
    return success_response(msg="更新名单成功")


@router.delete("/{lid}")
def delete_name_list(lid: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    name_list_service.delete_name_list(db, ctx, lid)
    return success_response(msg="删除名单成功")


@router.patch("/{lid}/status")
async def switch_name_list(lid: str, payload: SwitchNameList, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    name_list_service.switch_name_list(db, ctx, lid, form)
    return success_response(msg="名单状态修改成功")
