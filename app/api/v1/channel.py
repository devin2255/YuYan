from fastapi import APIRouter, Request

from sqlalchemy.orm import Session

from yuyan.app.api.deps import get_db
from yuyan.app.schemas.channel import CreateChannel, UpdateChannel
from yuyan.app.services import channel_service
from yuyan.app.services.response import success_response
from yuyan.app.services.serializer import to_dict
from yuyan.app.services.validators import FormProxy, parse_request_payload

router = APIRouter(prefix="/channel")


@router.get("/{cno}")
def get_channel(cno: str, db: Session = Depends(get_db)):
    channel = channel_service.get_channel(db, cno)
    return success_response(data=to_dict(channel))


@router.get("")
def get_channels(db: Session = Depends(get_db)):
    channels = channel_service.get_channels(db)
    return success_response(data=to_dict(channels))


@router.post("")
async def create_channel(request: Request, db: Session = Depends(get_db)):
    payload = await parse_request_payload(request)
    form_data = CreateChannel(**payload)
    form = FormProxy(**form_data.dict())
    channel_service.create_channel(db, form)
    return success_response(msg="新建渠道成功")


@router.put("/{cno}")
async def update_channel(cno: str, request: Request, db: Session = Depends(get_db)):
    payload = await parse_request_payload(request)
    form_data = UpdateChannel(**payload)
    form = FormProxy(**form_data.dict())
    channel_service.update_channel(db, cno, form)
    return success_response(msg="更新渠道成功")


@router.delete("/{cno}")
def delete_channel(cno: str, db: Session = Depends(get_db)):
    channel_service.delete_channel(db, cno)
    return success_response(msg="删除渠道成功")
