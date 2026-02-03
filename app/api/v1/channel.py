from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.channel import CreateChannel, UpdateChannel
from app.services import channel_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/channels")


@router.get("/{channel_id}")
def get_channel(channel_id: int, db: Session = Depends(get_db)):
    channel = channel_service.get_channel(db, channel_id)
    return success_response(data=to_dict(channel))


@router.get("")
def get_channels(db: Session = Depends(get_db)):
    channels = channel_service.get_channels(db)
    return success_response(data=to_dict(channels))


@router.post("")
async def create_channel(payload: CreateChannel, db: Session = Depends(get_db)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    channel_service.create_channel(db, form)
    return success_response(msg="新建渠道成功")


@router.put("/{channel_id}")
async def update_channel(channel_id: int, payload: UpdateChannel, db: Session = Depends(get_db)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    channel_service.update_channel(db, channel_id, form)
    return success_response(msg="更新渠道成功")


@router.delete("/{channel_id}")
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    channel_service.delete_channel(db, channel_id)
    return success_response(msg="删除渠道成功")
