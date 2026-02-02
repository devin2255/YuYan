import json
from typing import List

from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from yuyan.app.api.deps import get_ctx, get_db
from yuyan.app.schemas.name_list import CreateOrUpdateNameList, SwitchNameList
from yuyan.app.services import channel_service, game_service, name_list_service
from yuyan.app.services.response import success_response
from yuyan.app.services.serializer import to_dict
from yuyan.app.services.validators import FormProxy, parse_request_payload

router = APIRouter(prefix="/name_list")


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


def process_game_channel(db: Session, game_id, channel):
    game_ids = normalize_list(game_id)
    channel_nos = normalize_list(channel)

    if len(game_ids) > 5 or len(channel_nos) > 5:
        return [], []

    if game_ids:
        games = [game_service.get_game(db, gid) for gid in game_ids]
    else:
        games = [game_service.get_game(db, game_id)]

    if channel_nos:
        channels = [channel_service.get_channel(db, cno) for cno in channel_nos]
    else:
        channels = [channel_service.get_channel(db, channel)]
    return games, channels


@router.get("/{lid}")
def get_name_list(lid: str, db: Session = Depends(get_db)):
    data = name_list_service.get_name_list_by_name(db, lid)
    return to_dict(data)


@router.get("")
def get_name_lists(db: Session = Depends(get_db)):
    data = name_list_service.get_name_lists(db)
    return to_dict(data)


@router.post("")
async def create_name_list(request: Request, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = CreateOrUpdateNameList(**payload)
    form = FormProxy(**form_data.dict())
    games, channels = process_game_channel(db, form.game_id.data, form.channel.data)
    name_list_service.create_name_list(db, ctx, form, games, channels)
    return success_response(msg="新建名单成功")


@router.put("/{lid}")
async def update_name_list(lid: str, request: Request, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = CreateOrUpdateNameList(**payload)
    form = FormProxy(**form_data.dict())
    games, channels = process_game_channel(db, form.game_id.data, form.channel.data)
    name_list_service.update_name_list(db, ctx, lid, form, games, channels)
    return success_response(msg="更新名单成功")


@router.delete("/{lid}")
def delete_name_list(lid: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    name_list_service.delete_name_list(db, ctx, lid)
    return success_response(msg="删除名单成功")


@router.post("/swich/{lid}")
async def switch_name_list(lid: str, request: Request, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = SwitchNameList(**payload)
    form = FormProxy(**form_data.dict())
    name_list_service.switch_name_list(db, ctx, lid, form)
    return success_response(msg="名单状态修改成功")
